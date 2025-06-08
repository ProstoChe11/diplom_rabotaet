from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date
from sqlalchemy import JSON 
from sqlalchemy import event 

product_material_association = db.Table('product_material_association',
    db.Column('product_id', db.Integer, db.ForeignKey('product.id'), primary_key=True),
    db.Column('material_category_id', db.Integer, db.ForeignKey('material_category.id'), primary_key=True)
)

class MaterialCategory(db.Model):
    __tablename__ = 'material_category'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    code = db.Column(db.String(20), unique=True, nullable=False)
    unit = db.Column(db.String(20))
    description = db.Column(db.Text)
    stock_quantity = db.Column(db.Float, nullable=False, default=0.0) 
    average_cost_price = db.Column(db.Float, nullable=True, default=0.0) 
    
    norms = db.relationship('MaterialNorm', back_populates='material_category', lazy='dynamic') 
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'unit': self.unit,
            'description': self.description,
            'stock_quantity': self.stock_quantity,
            'average_cost_price': self.average_cost_price
        }

class MaterialConsumption(db.Model):
    __tablename__ = 'material_consumption'
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('material_category.id'))
    date = db.Column(db.Date, nullable=False)
    product_id = db.Column(db.Integer, nullable=False) 
    quantity = db.Column(db.Float, nullable=False)
    batch_number = db.Column(db.String(50))
    
    category = db.relationship('MaterialCategory', backref='consumptions') 

class MaterialNorm(db.Model): 
    __tablename__ = 'material_norm'
    id = db.Column(db.Integer, primary_key=True)
    
    material_category_id = db.Column(db.Integer, db.ForeignKey('material_category.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    norm_value = db.Column(db.Float, nullable=False)
    material_category = db.relationship("MaterialCategory", back_populates="norms")
    product = db.relationship("Product", back_populates="specifications")

    def __repr__(self):
        product_name = self.product.name if self.product else str(self.product_id)
        material_name = self.material_category.name if self.material_category else str(self.material_category_id)
        return f'<MaterialNorm product="{product_name}" material="{material_name}" value={self.norm_value}>'
    
class UserDashboard(db.Model):
    __tablename__ = 'user_dashboard'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True)
    config = db.Column(JSON, nullable=True) 
    
    user = db.relationship('User', backref=db.backref('dashboard', uselist=False))

class User(UserMixin, db.Model): 
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    full_name = db.Column(db.String(100))
    contact_info = db.Column(db.String(100))
    
    reports = db.relationship('Report', back_populates='user', lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

class Report(db.Model):
    __tablename__ = 'report'
    id = db.Column(db.Integer, primary_key=True)
    report_type = db.Column(db.String(50), nullable=False, default='material_stock') 
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    config = db.Column(JSON, nullable=True) 

    user = db.relationship('User', back_populates='reports')
    

    def __repr__(self):
        return f'<Report id={self.id} type={self.report_type} created_at={self.created_at.strftime("%Y-%m-%d")}>'

class Product(db.Model):
    __tablename__ = 'product'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    length = db.Column(db.Float, nullable=True) 
    width = db.Column(db.Float, nullable=True)  
    height = db.Column(db.Float, nullable=True) 
    dimension_unit = db.Column(db.String(10), nullable=True, default='мм')
    price = db.Column(db.Float, nullable=True, default=0.0) 

    material_categories = db.relationship(
        'MaterialCategory',
        secondary=product_material_association,
        backref=db.backref('associated_products', lazy='dynamic'),
        lazy='dynamic' 
    )

    specifications = db.relationship("MaterialNorm", back_populates="product", lazy='select', cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Product {self.name}>'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class MaterialReceipt(db.Model):
    __tablename__ = 'material_receipt'
    id = db.Column(db.Integer, primary_key=True)
    material_category_id = db.Column(db.Integer, db.ForeignKey('material_category.id'), nullable=False)
    quantity_received = db.Column(db.Float, nullable=False)
    receipt_date = db.Column(db.Date, nullable=False, default=date.today)
    document_ref = db.Column(db.String(100), nullable=True) 
    supplier = db.Column(db.String(150), nullable=True) 
    price_per_unit = db.Column(db.Float, nullable=True) 
    notes = db.Column(db.Text, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) 
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    material_category = db.relationship('MaterialCategory', backref=db.backref('receipts', lazy='dynamic'))
    user = db.relationship('User', backref=db.backref('material_receipts', lazy='dynamic'))

    def __repr__(self):
        return f'<MaterialReceipt {self.material_category.name if self.material_category else self.material_category_id} +{self.quantity_received} on {self.receipt_date}>'

class ProductionLog(db.Model):
    __tablename__ = 'production_log'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity_produced = db.Column(db.Integer, nullable=False)
    production_date = db.Column(db.Date, nullable=False, default=date.today)
    cost_per_unit_calculated = db.Column(db.Float, nullable=False) 
    total_cost_calculated = db.Column(db.Float, nullable=False)    
    
    config = db.Column(JSON, nullable=True) 
        
    notes = db.Column(db.Text, nullable=True) 
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) 
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    product = db.relationship('Product', backref=db.backref('production_logs', lazy='joined')) 
    user = db.relationship('User', backref=db.backref('production_logs_recorded', lazy='joined')) 

    def __repr__(self):
        return f'<ProductionLog ProductID: {self.product_id}, Qty: {self.quantity_produced}, Date: {self.production_date}>'
