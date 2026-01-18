from django.contrib import admin
from .models import (
    Course, Enrollment, CourseModule, Lesson, 
    Quiz, Question, Answer, LessonCompletion, QuizSubmission
)

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'educator', 'category', 'level', 'is_published', 'created_at']
    list_filter = ['is_published', 'level', 'category']
    search_fields = ['title', 'description']

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'enrolled_at', 'progress', 'completed']
    list_filter = ['completed', 'enrolled_at']
    search_fields = ['student__email', 'course__title']

@admin.register(CourseModule)
class CourseModuleAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'order']
    list_filter = ['course']
    search_fields = ['title']

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ['title', 'module', 'content_type', 'order', 'duration_minutes']
    list_filter = ['content_type']
    search_fields = ['title']

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ['title', 'lesson', 'passing_score']
    search_fields = ['title']

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['question_text', 'quiz', 'question_type', 'points', 'order']
    list_filter = ['question_type']
    search_fields = ['question_text']

@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ['answer_text', 'question', 'is_correct']
    list_filter = ['is_correct']

@admin.register(LessonCompletion)
class LessonCompletionAdmin(admin.ModelAdmin):
    list_display = ['student', 'lesson', 'completed_at']
    list_filter = ['completed_at']
    search_fields = ['student__email', 'lesson__title']

@admin.register(QuizSubmission)
class QuizSubmissionAdmin(admin.ModelAdmin):
    list_display = ['student', 'quiz', 'score', 'passed', 'submitted_at']
    list_filter = ['passed', 'submitted_at']
    search_fields = ['student__email', 'quiz__title']