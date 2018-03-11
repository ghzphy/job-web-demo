#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, abort,\
    current_app, redirect, url_for, flash, request
from flask_login import current_user
from ..decorators import company_required
from ..models import Job, db
from ..forms import EXP, JobForm

job = Blueprint('job', __name__, url_prefix='/job')


@job.route('/')
def index():
    page = request.args.get('page', default=1, type=int)
    # fil = request.args.get('filter', default=None, type=str)
    pagination = Job.query.filter(Job.is_enable.is_(True)).order_by(
            Job.created_at.desc()).paginate(
                page=page,
                per_page=current_app.config['JOB_INDEX_PER_PAGE'],
                error_out=False
            )
    return render_template('job/index.html', pagination=pagination, filter=EXP, active='job')


@job.route('/<int:job_id>')
def detail(job_id):
    job_data = Job.query.get_or_404(job_id)
    if not job_data.is_enable and job_data.company_id != current_user.id:
        abort(404)
    return render_template('job/detail.html', job=job_data)


@job.route('/create', methods=['GET', 'POST'])
@company_required
def create():
    form = JobForm()
    if form.validate_on_submit():
        company_id = current_user.id
        form.create_job(company_id)
        flash('职位创建成功', 'success')
        return redirect_job_index()
    return render_template('job/create.html', form=form)


@job.route('/<int:job_id>/edit', methods=['GET', 'POST'])
@company_required
def edit(job_id):
    job_data = Job.query.get_or_404(job_id)
    if job_data.company_id != current_user.id and not current_user.is_admin():
        abort(404)
    form = JobForm(obj=job_data)
    if form.validate_on_submit():
        form.update_job(job_data)
        flash('职位更新成功', 'success')
        return redirect_job_index()
    return render_template('job/edit.html', form=form, job_id=job_id)


@job.route('/<int:job_id>/delete', methods=['GET', 'POST'])
@company_required
def delete(job_id):
    job_data = Job.query.get_or_404(job_id)
    if job_data.company_id != current_user.id and not current_user.is_admin():
        abort(404)
    db.session.delete(job_data)
    db.session.commit()
    flash('职位删除成功', 'success')
    return redirect_job_index()


@job.route('<int:job_id>/disable')
@company_required
def disable(job_id):
    job_data = Job.query.get_or_404(job_id)
    if not current_user.is_admin() and current_user.id != job_data.company.id:
        abort(404)
    if not job_data.is_enable:
        flash('职位已下线', 'warning')
    else:
        job_data.is_enable = False
        db.session.add(job_data)
        db.session.commit()
        flash('职位下线成功', 'success')
    return redirect_job_index()


@job.route('<int:job_id>/enable')
@company_required
def enable(job_id):
    job_data = Job.query.get_or_404(job_id)
    if not current_user.is_admin() and current_user.id != job_data.company.id:
        abort(404)
    if job_data.is_enable:
        flash('职位已上线', 'warning')
    else:
        job_data.is_enable = True
        db.session.add(job_data)
        db.session.commit()
        flash('职位上线成功', 'success')
    return redirect_job_index()


def redirect_job_index():
    if current_user.is_admin():
        return redirect(url_for('admin.job'))
    elif current_user.is_company():
        return redirect(url_for('company.jobs'))
    else:
        return redirect(url_for('front.index'))
