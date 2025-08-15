from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from ..models import db, CodeSubmission
from ..utils.ai_utils import analyze_code_with_gemini, detect_plagiarism_hints
import os

bp = Blueprint('code', __name__)

@bp.route('/submit', methods=['GET', 'POST'])
@login_required
def submit_code():
    if request.method == 'POST':
        code_text = request.form.get('code_text', '').strip()
        language = request.form.get('language', 'python')
        
        if not code_text:
            flash('Please enter some code to review.')
            return redirect(url_for('code.submit_code'))
        
        # Analyze code with Gemini API
        try:
            feedback, score, comments = analyze_code_with_gemini(code_text, language)
            
            # Get detected language for storage
            from ..utils.ai_utils import detect_language
            detected_lang = detect_language(code_text)

            # Detect plagiarism hints
            plagiarism_hints = detect_plagiarism_hints(code_text)

            # Create submission
            submission = CodeSubmission(
                user_id=current_user.id,
                code_text=code_text,
                language=language,
                detected_language=detected_lang if detected_lang != 'unknown' else None,
                feedback=feedback,
                ai_score=score,
                comments=comments,
                plagiarism_hints=plagiarism_hints
            )
            db.session.add(submission)
            db.session.commit()
            
            # Check if this was a fallback analysis
            if "basic analysis" in feedback.lower() or "note: this is a basic analysis" in feedback.lower():
                flash('⚠️ AI service was temporarily unavailable. Showing basic analysis instead.')
            
            return redirect(url_for('code.view_feedback', submission_id=submission.id))
            
        except Exception as e:
            error_message = str(e)
            if "quota exceeded" in error_message.lower():
                flash(f'⚠️ {error_message}')
            elif "API key" in error_message.lower():
                flash(f'❌ {error_message}')
            else:
                flash(f'❌ Error analyzing code: {error_message}')
            return redirect(url_for('code.submit_code'))
    
    return render_template('submit_code.html')

@bp.route('/feedback/<int:submission_id>')
@login_required
def view_feedback(submission_id):
    submission = CodeSubmission.query.filter_by(id=submission_id, user_id=current_user.id).first_or_404()
    return render_template('feedback.html', submission=submission)

@bp.route('/history')
@login_required
def history():
    page = request.args.get('page', 1, type=int)
    language_filter = request.args.get('language', '')
    score_filter = request.args.get('score', '')
    
    query = CodeSubmission.query.filter_by(user_id=current_user.id)
    
    if language_filter:
        query = query.filter_by(language=language_filter)
    
    if score_filter:
        if score_filter == 'high':
            query = query.filter(CodeSubmission.ai_score >= 80)
        elif score_filter == 'medium':
            query = query.filter(CodeSubmission.ai_score.between(50, 79))
        elif score_filter == 'low':
            query = query.filter(CodeSubmission.ai_score < 50)
    
    submissions = query.order_by(CodeSubmission.timestamp.desc()).paginate(
        page=page, per_page=10, error_out=False
    )
    
    return render_template('history.html', submissions=submissions, 
                         language_filter=language_filter, score_filter=score_filter) 