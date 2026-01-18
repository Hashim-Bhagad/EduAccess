from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Course, Enrollment, Lesson

def home(request):
    """Landing page view"""
    return render(request, 'home.html')


@login_required
def dashboard(request):
    """Dashboard view for authenticated users"""
    user = request.user
    
    context = {
        'user': user,
    }
    
    if user.user_type == 'student':
        # Get student's enrolled courses
        enrollments = Enrollment.objects.filter(student=user).select_related('course')
        enrolled_courses = [enrollment.course for enrollment in enrollments]
        context['enrolled_courses'] = enrolled_courses
        context['total_courses'] = enrollments.count()
        context['completed_courses'] = enrollments.filter(completed=True).count()
        
        # Get available courses (published, not enrolled)
        enrolled_course_ids = [course.id for course in enrolled_courses]
        available_courses = Course.objects.filter(
            is_published=True
        ).exclude(
            id__in=enrolled_course_ids
        ).select_related('educator')
        context['available_courses'] = available_courses
    else:
        # Get educator's created courses
        context['created_courses'] = Course.objects.filter(educator=user)
        context['total_courses'] = context['created_courses'].count()
        context['total_students'] = Enrollment.objects.filter(
            course__educator=user
        ).values('student').distinct().count()
    
    return render(request, 'dashboard.html', context)


def course_list(request):
    """List all published courses"""
    courses = Course.objects.filter(is_published=True).select_related('educator')
    return render(request, 'courses/course_list.html', {'courses': courses})


@login_required
def course_detail(request, course_id):
    """View course details"""
    course = get_object_or_404(Course, id=course_id, is_published=True)
    
    # Check if user is enrolled
    is_enrolled = False
    if request.user.user_type == 'student':
        is_enrolled = Enrollment.objects.filter(
            student=request.user,
            course=course
        ).exists()
    
    context = {
        'course': course,
        'is_enrolled': is_enrolled,
        'modules': course.modules.all(),
    }
    
    return render(request, 'courses/course_detail.html', context)


@login_required
def enroll_course(request, course_id):
    """Enroll student in a course"""
    if request.user.user_type != 'student':
        messages.error(request, 'Only students can enroll in courses.')
        return redirect('core:dashboard')
    
    course = get_object_or_404(Course, id=course_id, is_published=True)
    
    # Create enrollment if doesn't exist
    enrollment, created = Enrollment.objects.get_or_create(
        student=request.user,
        course=course
    )
    
    if created:
        messages.success(request, f'Successfully enrolled in {course.title}!')
    else:
        messages.info(request, f'You are already enrolled in {course.title}.')
    
    return redirect('core:course_detail', course_id=course_id)


@login_required
def course_create(request):
    """Allow educators to create a new course"""
    if request.user.user_type != 'educator':
        messages.error(request, "Only educators can create courses.")
        return redirect('core:dashboard')
    
    if request.method == 'POST':
        from .forms import CourseForm
        form = CourseForm(request.POST, request.FILES)
        if form.is_valid():
            course = form.save(commit=False)
            course.educator = request.user
            course.save()
            messages.success(request, f"Course '{course.title}' created successfully!")
            return redirect('core:dashboard') # Later redirect to course edit/module manager
    else:
        from .forms import CourseForm
        form = CourseForm()
    
    return render(request, 'core/course_form.html', {'form': form, 'title': 'Create New Course'})

@login_required
def course_edit(request, course_id):
    """View to edit an existing course"""
    course = get_object_or_404(Course, id=course_id)
    # Ensure only the creator can edit
    if request.user != course.educator:
        messages.error(request, "You do not have permission to edit this course.")
        return redirect('core:course_detail', course_id=course.id)
        
    from .forms import CourseForm

    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, "Course updated successfully!")
            return redirect('core:course_detail', course_id=course.id)
    else:
        form = CourseForm(instance=course)
        
    return render(request, 'core/course_form.html', {'form': form, 'title': f'Edit {course.title}'})

@login_required
def course_delete(request, course_id):
    """View to delete a course"""
    course = get_object_or_404(Course, id=course_id)
    if request.user != course.educator:
        messages.error(request, "You do not have permission to delete this course.")
        return redirect('core:course_detail', course_id=course.id)
        
    if request.method == 'POST':
        course.delete()
        messages.success(request, "Course deleted successfully.")
        return redirect('core:dashboard')
        
    return render(request, 'core/course_confirm_delete.html', {'course': course})



@login_required
def module_create(request, course_id):
    """Add a module to a course"""
    course = get_object_or_404(Course, id=course_id)
    if request.user != course.educator:
        messages.error(request, "Permission denied.")
        return redirect('core:dashboard')
        
    if request.method == 'POST':
        from .forms import ModuleForm
        form = ModuleForm(request.POST)
        if form.is_valid():
            module = form.save(commit=False)
            module.course = course
            module.save()
            messages.success(request, "Module added!")
            return redirect('core:course_detail', course_id=course.id)
    else:
        from .forms import ModuleForm
        form = ModuleForm()
        
    return render(request, 'core/module_form.html', {'form': form, 'course': course})


@login_required
def lesson_create(request, module_id):
    """Add a lesson to a module"""
    from .models import CourseModule
    module = get_object_or_404(CourseModule, id=module_id)
    if request.user != module.course.educator:
        messages.error(request, "Permission denied.")
        return redirect('core:dashboard')
        
    if request.method == 'POST':
        from .forms import LessonForm
        form = LessonForm(request.POST, request.FILES)
        if form.is_valid():
            lesson = form.save(commit=False)
            lesson.module = module
            lesson.save()
            messages.success(request, "Lesson added!")
            
            if lesson.content_type == 'quiz':
                return redirect('core:quiz_create', lesson_id=lesson.id)
                
            return redirect('core:course_detail', course_id=module.course.id)
    else:
        from .forms import LessonForm
        initial_data = {}
        if 'type' in request.GET:
            initial_data['content_type'] = request.GET['type']
        form = LessonForm(initial=initial_data)
        
    return render(request, 'core/lesson_form.html', {'form': form, 'module': module})


@login_required
def quiz_create(request, lesson_id):
    """Create a quiz for a specific lesson"""
    from .models import Lesson
    lesson = get_object_or_404(Lesson, id=lesson_id)
    if request.user != lesson.module.course.educator:
        messages.error(request, "Permission denied.")
        return redirect('core:dashboard')
        
    # Check if quiz already exists
    if hasattr(lesson, 'quiz'):
        return redirect('core:quiz_detail', quiz_id=lesson.quiz.id)

    if request.method == 'POST':
        from .forms import QuizForm
        form = QuizForm(request.POST)
        if form.is_valid():
            quiz = form.save(commit=False)
            quiz.lesson = lesson
            quiz.save()
            messages.success(request, "Quiz created! Now add some questions.")
            return redirect('core:question_create', quiz_id=quiz.id)
    else:
        from .forms import QuizForm
        form = QuizForm(initial={'title': f"Quiz: {lesson.title}"})
        
    return render(request, 'core/quiz_form.html', {'form': form, 'lesson': lesson})


@login_required
def question_create(request, quiz_id):
    """Add questions to a quiz"""
    from .models import Quiz
    quiz = get_object_or_404(Quiz, id=quiz_id)
    if request.user != quiz.lesson.module.course.educator:
         messages.error(request, "Permission denied.")
         return redirect('core:dashboard')
         
    if request.method == 'POST':
        from .forms import QuestionForm
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.quiz = quiz
            question.save()
            
            # Handle MCQ Answers
            if question.question_type == 'multiple_choice':
                from .models import Answer
                correct_idx = int(request.POST.get('correct_answer', 0))
                
                # We expect up to 4 answers
                for i in range(4):
                    answer_text = request.POST.get(f'answer_{i}')
                    if answer_text and answer_text.strip():
                        Answer.objects.create(
                            question=question,
                            answer_text=answer_text.strip(),
                            is_correct=(i == correct_idx)
                        )
            
            messages.success(request, "Question added!")
            
            if 'add_another' in request.POST:
                return redirect('core:question_create', quiz_id=quiz.id)
            else:
                return redirect('core:course_detail', course_id=quiz.lesson.module.course.id)
    else:
        from .forms import QuestionForm
        # Auto-increment order
        last_question = quiz.questions.last()
        next_order = last_question.order + 1 if last_question else 1
        form = QuestionForm(initial={'order': next_order})
        
    return render(request, 'core/question_form.html', {'form': form, 'quiz': quiz})

@login_required
def quiz_detail(request, quiz_id):
    """View for students to take a quiz or educators to preview it"""
    from .models import Quiz, Answer
    quiz = get_object_or_404(Quiz, id=quiz_id)
    
    # Check enrollment or ownership
    is_educator = (request.user == quiz.lesson.module.course.educator)
    # TODO: Check enrollment for students
    
    if request.method == 'POST':
        # Handle quiz submission
        score = 0
        total_points = 0
        passed = False
        
        # Calculate score
        for question in quiz.questions.all():
            total_points += question.points
            submitted_answer_id = request.POST.get(f'question_{question.id}')
            
            if question.question_type == 'multiple_choice' and submitted_answer_id:
                try:
                    selected_answer = question.answers.get(id=submitted_answer_id)
                    if selected_answer.is_correct:
                        score += question.points
                except:
                    pass
        
        # Calculate percentage
        percentage = 0
        if total_points > 0:
            percentage = (score / total_points) * 100
            
        passed = percentage >= quiz.passing_score
        
        # Save submission
        if not is_educator:
            from .models import QuizSubmission
            QuizSubmission.objects.create(
                student=request.user,
                quiz=quiz,
                score=percentage,
                passed=passed
            )
            
        if passed:
            messages.success(request, f"Congratulations! You passed with {percentage:.1f}%")
        else:
            messages.warning(request, f"You scored {percentage:.1f}%. You need {quiz.passing_score}% to pass.")
            
        return redirect('core:quiz_detail', quiz_id=quiz.id)

    # Check for previous submission
    last_submission = None
    if not is_educator:
        from .models import QuizSubmission
        last_submission = QuizSubmission.objects.filter(student=request.user, quiz=quiz).order_by('-submitted_at').first()

    return render(request, 'core/quiz_detail.html', {
        'quiz': quiz, 
        'is_educator': is_educator,
        'last_submission': last_submission
    })


@login_required
def lesson_detail(request, lesson_id):
    """View to content of a specific lesson (Video/PDF/Text)"""
    lesson = get_object_or_404(Lesson, id=lesson_id)
    
    # Check if user is enrolled or is course creator
    is_creator = (request.user == lesson.module.course.educator)
    if not is_creator:
        is_enrolled = lesson.module.course.enrollments.filter(student=request.user).exists()
        if not is_enrolled:
            messages.error(request, "You must be enrolled to view this lesson.")
            return redirect('core:course_detail', course_id=lesson.module.course.id)

    # Check for completion
    from .models import LessonCompletion
    is_completed = False
    if not is_creator:
        is_completed = LessonCompletion.objects.filter(student=request.user, lesson=lesson).exists()

    context = {
        'lesson': lesson,
        'is_creator': is_creator,
        'is_completed': is_completed,
    }
    return render(request, 'core/lesson_detail.html', context)
    

@login_required
def mark_lesson_complete(request, lesson_id):
    """Mark a lesson as complete"""
    if request.method == 'POST':
        lesson = get_object_or_404(Lesson, id=lesson_id)
        # Verify enrollment
        is_enrolled = lesson.module.course.enrollments.filter(student=request.user).exists()
        
        if is_enrolled:
            from .models import LessonCompletion
            LessonCompletion.objects.get_or_create(student=request.user, lesson=lesson)
            messages.success(request, "Lesson marked as complete!")
        
        return redirect('core:course_detail', course_id=lesson.module.course.id)
    
    return redirect('core:dashboard')



