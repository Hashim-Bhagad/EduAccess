from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Course, Enrollment

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
        context['enrolled_courses'] = [enrollment.course for enrollment in enrollments]
        context['total_courses'] = enrollments.count()
        context['completed_courses'] = enrollments.filter(completed=True).count()
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