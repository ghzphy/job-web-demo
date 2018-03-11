from flask_ckeditor import CKEditorField
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import IntegerField, PasswordField, SelectField, \
    StringField, SubmitField, TextAreaField, ValidationError, BooleanField
from wtforms.validators import Email, EqualTo, Regexp, Length, URL, DataRequired
from .models import User, Company, db, Job, FINANCE_STAGE, FIELD, EDUCATION, EXP
from .app import uploaded_pdf


class RegisterUserForm(FlaskForm):

    name = StringField('姓名', validators=[DataRequired(message='请填写内容'),
                                         Length(4, 16, message='长度须在4～16个字符之间')])
    email = StringField('邮箱', validators=[DataRequired(message='请填写内容'),
                                          Email(message='请输入合法的email地址')])
    password = PasswordField('密码', validators=[DataRequired(message='请填写密码'),
                                               Length(6, 24, message='长度须在6～24个字符之间'),
                                               Regexp(r'^[a-zA-Z]+\w+', message='仅限使用英文、数字、下划线，并以英文开头')])
    repeat_password = PasswordField('重复密码', validators=[DataRequired(message='请填写密码'),
                                                        EqualTo('password', message='两次密码不一致')])
    submit = SubmitField('提交')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('邮箱已被其他账号使用')

    def create_user(self):
        user = User()
        user.name = self.name.data
        user.email = self.email.data
        user.password = self.password.data
        db.session.add(user)
        db.session.commit()
        return user


class RegisterCompanyForm(FlaskForm):

    name = StringField('企业名称', validators=[DataRequired(message='请填写内容'),
                                           Length(4, 64, message='长度要在4～64个字符之间')])
    email = StringField('邮箱', validators=[DataRequired(message='请填写内容'),
                                          Email(message='请输入合法的Email地址')])
    password = PasswordField('密码', validators=[DataRequired(message='请填写密码'),
                                               Length(6, 24, message='长度须在6～24个字符之间'),
                                               Regexp(r'^[a-zA-Z]+\w+', message='仅限使用英文、数字、下划线，并以英文开头')])
    repeat_password = PasswordField('重复密码', validators=[DataRequired(message='请填写密码'),
                                                        EqualTo('password', message='两次密码不一致')])
    submit = SubmitField('提交')

    def validate_email(self, field):
        if Company.query.filter_by(email=field.data).first():
            raise ValidationError('邮箱已被其他账号使用')

    def create_company(self):
        company = Company()
        company.name = self.name.data
        company.email = self.email.data
        company.password = self.password.data
        db.session.add(company)
        db.session.commit()
        return company


class LoginForm(FlaskForm):

    email = StringField('邮箱', validators=[DataRequired(message='请填写内容'),
                                          Email(message='请输入合法的email地址')])
    password = PasswordField('密码', validators=[DataRequired(message='请填写密码'),
                                               Length(6, 24, message='长度须在6～24个字符之间')])
    remember_me = BooleanField('记住登录状态')
    submit = SubmitField('登录')


class UserDetailForm(FlaskForm):

    resume = FileField('简历上传', validators=[
                FileAllowed('pdf', '仅限PDF格式！'),
                FileRequired('文件未选择')])
    submit = SubmitField('提交')

    def update_detail(self, user):
        self.populate_obj(user)
        filename = uploaded_pdf.save(self.resume.data)
        user.resume = uploaded_pdf.url(filename)
        print(filename, uploaded_pdf.url(filename), self.resume.data)
        db.session.add(user)
        db.session.commit()


class CompanyDetailForm(FlaskForm):

    address = StringField('办公地址', validators=[DataRequired(message='请填写内容'),
                                              Length(0, 128, message='超过128个字符')])
    logo = StringField('公司Logo', validators=[DataRequired(message='请填写内容'),
                                             Length(1, 256, message='请确认您输入的Logo')])
    finance_stage = SelectField('融资阶段', choices=[(i, i) for i in FINANCE_STAGE])
    field = SelectField('行业领域', choices=[(i, i) for i in FIELD])
    website = StringField('公司网址', validators=[DataRequired(message='请填写内容'),
                                              URL(message='请确认您输入的网址')])
    description = StringField('公司简介', validators=[DataRequired(message='请填写内容')])
    details = CKEditorField('公司详情', validators=[DataRequired(message='请填写内容')])
    submit = SubmitField('提交')

    def update_detail(self, company):
        self.populate_obj(company)
        db.session.add(company)
        db.session.commit()


class JobForm(FlaskForm):

    name = StringField('职位名称', validators=[DataRequired(message='请填写内容'), Length(4, 32)])
    salary_min = IntegerField('最低薪水（单位：千元）', validators=[DataRequired(message='请填写整数')])
    salary_max = IntegerField('最高薪水（单位：千元）', validators=[DataRequired(message='请填写整数')])
    city = StringField('工作城市', validators=[DataRequired(message='请填写内容'),
                                           Length(0, 8, message='超过8个字符')])
    tags = StringField('职位标签(用逗号区隔)', validators=[Length(0, 64)])
    exp = SelectField('工作年限', choices=[(i, i) for i in EXP])
    education = SelectField('学历要求', choices=[(i, i) for i in EDUCATION])
    treatment = TextAreaField('职位待遇', validators=[Length(0, 256, message='超过256个字符')])
    description = CKEditorField('职位描述', validators=[DataRequired(message='请填写内容')])
    is_enable = SelectField('发布', choices=[('True', '立即发布'), ('False', '暂不发布')])
    submit = SubmitField('提交')

    def validate_salary_min(self, field):
        if field.data <= 0 or field.data > 100:
            raise ValidationError('须填写0～100之间的整数')
        if self.salary_max and field.data > self.salary_max:
            raise ValidationError('需要小于最高薪水')

    def validate_salary_max(self, field):
        if 0 < field.data <= 100:
            raise ValidationError('须填写0~100之间的整数')
        if self.salary_min and field.data < self.salary_min:
            raise ValidationError('需要大于最低薪水')

    def create_job(self, company_id):
        job = Job()
        self.populate_obj(job)
        job.company_id = company_id
        db.session.add(job)
        db.session.commit()
        return job

    def update_job(self, job):
        self.populate_obj(job)
        db.session.add(job)
        db.session.commit()
        return job


class CompanyDeliveryForm(FlaskForm):

    job_id = StringField('')