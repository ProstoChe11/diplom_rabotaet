from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, TextAreaField, DateField, FloatField, SubmitField, IntegerField, SelectMultipleField 
from wtforms.validators import DataRequired, Length, EqualTo, Optional, NumberRange
from datetime import date
from wtforms.widgets import PasswordInput
from app.models import MaterialCategory, Product 
from flask import request

class MaterialCategoryForm(FlaskForm):
    name = StringField('Название*', validators=[DataRequired(message="Поле 'Название' обязательно")]) 
    code = StringField('Код*', validators=[DataRequired(message="Поле 'Код' обязательно")])
    unit = SelectField('Единица измерения*', choices=[ 
        ('kg', 'Килограммы'),
        ('g', 'Граммы'),
        ('l', 'Литр'),
        ('ml', 'Миллилитр'),
        ('pcs', 'Штуки'),
        ('m', 'Метры'),
        ('sq.m', 'кв. метры'), 
        ('item', 'шт.') 
    ], validators=[DataRequired(message="Выберите единицу измерения")])
    description = TextAreaField('Описание', validators=[Optional()]) 
    stock_quantity = FloatField('Начальное количество на складе*', 
                                validators=[DataRequired(message="Укажите количество"), 
                                            NumberRange(min=0, message="Количество не может быть отрицательным")],
                                default=0.0,
                                render_kw={"placeholder": "0.0", "step": "any"})
    submit = SubmitField('Сохранить категорию')

class MaterialNormForm(FlaskForm):
    product_id = SelectField('Продукт*', coerce=int, validators=[DataRequired(message="Выберите продукт")])
    material_category_id = SelectField('Категория материала*', coerce=int, validators=[DataRequired(message="Выберите категорию материала")])
    norm_value = FloatField('Норма расхода (на 1 ед. продукта)*', 
                            validators=[DataRequired(message="Укажите норму расхода"), 
                                        NumberRange(min=0.000001, message="Норма должна быть больше нуля")], 
                            render_kw={"step": "any", "placeholder": "0.000"}) 
    submit = SubmitField('Сохранить норму')

    def __init__(self, *args, **kwargs):
        super(MaterialNormForm, self).__init__(*args, **kwargs)
        active_products = Product.query.order_by(Product.name).all()
        self.product_id.choices = [(p.id, p.name) for p in active_products]
        if not active_products:
            self.product_id.choices.insert(0, (0, "--- Добавьте продукты ---"))
            if request.method == 'GET' and not self.product_id.data : self.product_id.data = 0


        active_material_categories = MaterialCategory.query.order_by(MaterialCategory.name).all()
        self.material_category_id.choices = [(mc.id, f"{mc.code} - {mc.name}") for mc in active_material_categories]
        if not active_material_categories:
            self.material_category_id.choices.insert(0, (0, "--- Добавьте категории материалов ---"))
            if request.method == 'GET' and not self.material_category_id.data : self.material_category_id.data = 0


class ProductForm(FlaskForm):
    name = StringField('Название продукта*', validators=[
        DataRequired(message="Поле обязательно для заполнения"),
        Length(min=3, max=100, message="Название должно быть от 3 до 100 символов")
    ], render_kw={"placeholder": "Введите название продукта"})
    
    description = TextAreaField('Описание', validators=[
        Optional(),
        Length(max=500, message="Максимальная длина 500 символов")
    ], render_kw={"placeholder": "Дополнительная информация о продукте", "rows": 3})
    
    price = FloatField('Цена за единицу', validators=[Optional(), NumberRange(min=0.0, message="Цена не может быть отрицательной.")], default=0.0, render_kw={"placeholder": "0.00", "step": "0.01"})
    length = FloatField('Длина', validators=[Optional(), NumberRange(min=0)], render_kw={"placeholder": "0.0"})
    width = FloatField('Ширина', validators=[Optional(), NumberRange(min=0)], render_kw={"placeholder": "0.0"})
    height = FloatField('Высота', validators=[Optional(), NumberRange(min=0)], render_kw={"placeholder": "0.0"})
    dimension_unit = SelectField('Единица измерения габаритов', choices=[
        ('мм', 'Миллиметры (мм)'),
        ('см', 'Сантиметры (см)'),
        ('м', 'Метры (м)'),
    ], validators=[Optional()], default='мм')
    
    submit = SubmitField('Сохранить продукт')

class LoginForm(FlaskForm):
    username = StringField('Логин', validators=[
        DataRequired(message="Поле обязательно для заполнения"),
        Length(min=3, max=30, message="Логин должен быть от 3 до 30 символов")
    ], render_kw={"placeholder": "Введите ваш логин"})
    
    password = PasswordField('Пароль', validators=[
        DataRequired(message="Поле обязательно для заполнения")
    ], widget=PasswordInput(), render_kw={"placeholder": "Введите пароль"})
    
    submit = SubmitField('Войти', render_kw={"class": "btn btn-primary"})

class UserForm(FlaskForm):
    username = StringField('Логин*', validators=[
        DataRequired(message="Поле обязательно для заполнения"),
        Length(min=3, max=30, message="Логин должен быть от 3 до 30 символов")
    ], render_kw={"placeholder": "Уникальное имя пользователя"})
    
    password = PasswordField('Пароль', validators=[
        Optional(),
        Length(min=6, max=50, message="Пароль должен быть от 6 до 50 символов")
    ], widget=PasswordInput(), 
       render_kw={"placeholder": "Оставьте пустым, чтобы не менять"})
    
    confirm_password = PasswordField('Подтверждение пароля', 
                                   validators=[EqualTo('password', message="Пароли должны совпадать")],
                                   widget=PasswordInput())
    
    role = SelectField('Роль*', choices=[
        ('admin', 'Администратор'), 
        ('accountant', 'Бухгалтер'), 
        ('analyst', 'Финансовый аналитик')
    ], validators=[DataRequired(message="Выберите роль пользователя")])
    
    full_name = StringField('ФИО*', validators=[
        DataRequired(message="Поле обязательно для заполнения"),
        Length(max=100, message="Максимальная длина 100 символов")
    ], render_kw={"placeholder": "Иванов Иван Иванович"})
    
    contact_info = StringField('Контактная информация', validators=[
        Length(max=100, message="Максимальная длина 100 символов")
    ], render_kw={"placeholder": "Email или телефон"})
    
    submit = SubmitField('Сохранить', render_kw={"class": "btn btn-success"})

class ComparePeriodsForm(FlaskForm):
    period1_start = DateField('Начало периода 1', validators=[DataRequired()])
    period1_end = DateField('Конец периода 1', validators=[DataRequired()])
    period2_start = DateField('Начало периода 2', validators=[DataRequired()])
    period2_end = DateField('Конец периода 2', validators=[DataRequired()])
    submit = SubmitField('Сравнить')


class ReportForm(FlaskForm):
    
    pass 


class SearchForm(FlaskForm): 
    
    date_from = DateField('С', 
                         validators=[Optional()],
                         render_kw={"type": "date"})
    
    date_to = DateField('По', 
                       validators=[Optional()],
                       render_kw={"type": "date"})
    
    search = StringField('Поиск по комментарию/описанию', 
                        validators=[Optional(), Length(max=100)],
                        render_kw={"placeholder": "Введите текст для поиска"})
    
    submit = SubmitField('Найти', render_kw={"class": "btn btn-secondary"})

class ProduceProductForm(FlaskForm):
    product_id = SelectField('Продукт для производства*', coerce=int, validators=[DataRequired()])
    quantity_to_produce = IntegerField('Количество для производства*', 
                                       validators=[DataRequired(), NumberRange(min=1, message="Количество должно быть не меньше 1")],
                                       default=1)
    production_date = DateField('Дата производства', default=date.today, validators=[DataRequired()])
    notes = TextAreaField('Примечания (например, номер партии)', validators=[Optional(), Length(max=255)])
    submit = SubmitField('Произвести продукцию')

    def __init__(self, *args, **kwargs):
        super(ProduceProductForm, self).__init__(*args, **kwargs)
        products_with_specs = Product.query.filter(Product.specifications.any()).order_by(Product.name).all()
        self.product_id.choices = [(p.id, p.name) for p in products_with_specs]
        if not products_with_specs:
            self.product_id.choices.insert(0, (0, "--- Нет продуктов со спецификациями ---"))
            if request.method == 'GET' and not self.product_id.data : self.product_id.data = 0

class MaterialReceiptForm(FlaskForm):
    material_category_id = SelectField(
        'Категория материала*', 
        coerce=int, 
        validators=[DataRequired(message="Выберите категорию материала.")]
    )
    quantity_received = FloatField(
        'Количество оприходованного материала*', 
        validators=[
            DataRequired(message="Укажите количество."), 
            NumberRange(min=0.000001, message="Количество должно быть больше нуля.")
        ],
        render_kw={"step": "any", "placeholder": "0.000"}
    )
    receipt_date = DateField(
        'Дата оприходования*', 
        default=date.today, 
        validators=[DataRequired(message="Укажите дату.")]
    )
    document_ref = StringField(
        'Документ-основание (накладная, счет)', 
        validators=[Optional(), Length(max=100)],
        render_kw={"placeholder": "Например, ТН-123 от 01.01.2024"}
    )
    supplier = StringField(
        'Поставщик', 
        validators=[Optional(), Length(max=150)],
        render_kw={"placeholder": "Название компании или ФИО"}
    )
    price_per_unit = FloatField( 
        'Цена за единицу*', 
        validators=[DataRequired(message="Укажите цену за единицу."), NumberRange(min=0.00, message="Цена не может быть отрицательной.")],
        render_kw={"step": "any", "placeholder": "0.00"}
    )
    notes = TextAreaField(
        'Примечания', 
        validators=[Optional(), Length(max=500)], 
        render_kw={"rows": 3, "placeholder": "Дополнительная информация..."}
    )
    submit = SubmitField('Оприходовать материал')

    def __init__(self, *args, **kwargs):
        super(MaterialReceiptForm, self).__init__(*args, **kwargs)
        active_material_categories = MaterialCategory.query.order_by(MaterialCategory.name).all()
        
        choices = []
        if not active_material_categories:
            choices.append((0, "--- Сначала добавьте категории материалов ---"))
        else:
            
            choices = [
                (mc.id, f"{mc.name} ({mc.code}) - ост: {mc.stock_quantity:.2f} {mc.unit if mc.unit else ''}, ср.ц: {(mc.average_cost_price if mc.average_cost_price is not None else 0):.2f} ₽") 
                for mc in active_material_categories
            ]
            choices.insert(0, (0, "--- Выберите категорию ---"))

        self.material_category_id.choices = choices
        
        if not self.material_category_id.data and request.method == 'GET': 
            self.material_category_id.data = 0 