from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout, login
from django.contrib import messages
from django.contrib.auth.models import User, Group
from django.db.models import Count, Q
from django.db.models.functions import TruncMonth
from django.core.paginator import Paginator
from .models import Document, Category
from .models import Notification
from django.http import JsonResponse

# ==========notification backend===========#

def create_notification(user, message):
    Notification.objects.create(user=user, message=message)

from django.http import JsonResponse
def mark_notifications_read(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return JsonResponse({"status": "ok"})    


# ================= ROLE CHECK FUNCTIONS =================

def is_staff_user(user):
    return user.groups.filter(name="Staff").exists()

def is_student(user):
    return user.groups.filter(name="Student").exists()


# ================= REGISTER =================

def register(request):

    if request.method == 'POST':

        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('register')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return redirect('register')

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1,
            first_name=first_name,
            last_name=last_name
        )

        group, created = Group.objects.get_or_create(name="Student")
        user.groups.add(group)

        messages.success(request, "Account created successfully!")
        return redirect('login')

    return render(request, 'registration/register.html')


# ================= LOGIN =================

def login_view(request):

    if request.method == "POST":

        identifier = request.POST.get("username")
        password = request.POST.get("password")

        user = None

        if "@" in identifier:
            try:
                user = User.objects.get(email=identifier)
            except User.DoesNotExist:
                user = None
        else:
            try:
                user = User.objects.get(username=identifier)
            except User.DoesNotExist:
                user = None

        if user and user.check_password(password):

            login(request, user)

            if user.is_superuser:
                return redirect('admin_dashboard')

            if user.groups.filter(name="Staff").exists():
                return redirect('staff_dashboard')

            if user.groups.filter(name="Student").exists():
                return redirect('student_dashboard')

            else:
                return redirect('home')

        else:
            messages.error(request, "Invalid username/email or password.")

    return render(request, 'registration/login.html')


# ================= HOME =================

@login_required
def home(request):

    user = request.user
    can_upload = user.is_superuser or is_staff_user(user)
    lecturers = User.objects.filter(groups__name="Staff")
    

    if user.is_superuser:
        documents = Document.objects.all()

    elif is_staff_user(user):

        documents = Document.objects.filter(
            Q(visibility='public') |
            Q(visibility='staff') |
            Q(visibility='shared', shared_with=user) |
            Q(uploaded_by=user)
        ).distinct()

    elif is_student(user):

        documents = Document.objects.filter(
            Q(visibility='public') |
            Q(visibility='student') |
            Q(visibility='shared', shared_with=user) |
            Q(uploaded_by=user)
        ).distinct()

    else:
        documents = Document.objects.filter(uploaded_by=user)

    documents = documents.select_related(
        "category", "uploaded_by"
    ).order_by('-created_at')


    category_filter = request.GET.get('category')
    search_query = request.GET.get('q')

    if category_filter and category_filter.isdigit():
        documents = documents.filter(category_id=int(category_filter))
    else:
        category_filter = ""

    if search_query and search_query.lower() != "none":
        documents = documents.filter(title__icontains=search_query)
    else:
        search_query = ""


    paginator = Paginator(documents, 5)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)


    # ================== UPLOAD=====

    if request.method == "POST" and can_upload:

        title = request.POST.get("title")
        file = request.FILES.get("file")
        visibility = request.POST.get("visibility")
        category_id = request.POST.get("category")

        if title and file:

            Document.objects.create(
                title=title,
                file=file,
                uploaded_by=user,
                visibility=visibility,
                category_id=category_id if category_id else None
            )

            messages.success(request, "Document uploaded successfully.")
            create_notification(request.user, f"You uploaded '{title}'")

            return redirect("home")

        else:
            messages.error(request, "All fields are required.")


    categories = Category.objects.all()

    total_documents = Document.objects.count()
    total_categories = Category.objects.count()
    my_uploads = Document.objects.filter(uploaded_by=user).count()
    public_documents = Document.objects.filter(visibility='public').count()


    context = {
        'documents': page_obj,
        'page_obj': page_obj,
        'categories': categories,
        'can_upload': can_upload,
        'is_admin': user.is_superuser,
        'is_staff': is_staff_user(user),
        'is_student': is_student(user),
        'selected_category': category_filter,
        'search_query': search_query,

        'total_documents': total_documents,
        'total_categories': total_categories,
        'my_uploads': my_uploads,
        'public_documents': public_documents,

        'lecturers': lecturers,
    }

    return render(request, 'documents/home.html', context)


# ================= UPLOAD DOCUMENT VIEW =================


@login_required
def upload_document(request):

    if not (request.user.is_superuser or is_staff_user(request.user)):
        messages.error(request, "You are not allowed to upload.")
        return redirect('home')

    if request.method == "POST":

        title = request.POST.get("title")
        file = request.FILES.get("file")
        visibility = request.POST.get("visibility")
        category_id = request.POST.get("category")

        if title and file:

            Document.objects.create(
                title=title,
                file=file,
                uploaded_by=request.user,
                visibility=visibility,
                category_id=category_id if category_id else None
            )

            messages.success(request, "Document uploaded successfully.")
            return redirect("home")

        else:
            messages.error(request, "All fields are required.")

    categories = Category.objects.all()

    return render(request, "documents/upload.html", {
        "categories": categories
    })


# ================= STAFF DASHBOARD =================

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.db.models import Q
from .models import Document, Notification


@login_required
def staff_dashboard(request):
    """
    Staff Dashboard View
    - Shows documents based on visibility rules
    - Shows latest notifications
    - Adds dashboard stats (NEW)
    """

    # =========================
    # 🚫 ACCESS CONTROL
    # =========================
    if not is_staff_user(request.user):
        return redirect('home')


    # =========================
    # 🔔 NOTIFICATIONS
    # =========================
    notifications = Notification.objects.filter(
        user=request.user
    ).order_by('-created_at')[:5]


    # =========================
    # 📄 DOCUMENTS (YOUR LOGIC - KEPT)
    # =========================
    documents = Document.objects.filter(
        Q(visibility='public') |
        Q(visibility='staff') |
        Q(uploaded_by=request.user) |
        Q(visibility='shared', shared_with=request.user)
    ).distinct().order_by('-created_at')


    # =========================
    # 📊 STATS (NEW - SAFE)
    # =========================

    # Total documents user can SEE (same filter as above)
    total_docs = documents.count()

    # Documents uploaded by THIS user
    my_docs = Document.objects.filter(uploaded_by=request.user).count()

    # Shared documents (only if field exists)
    try:
        shared_docs = Document.objects.filter(
            visibility='shared',
            shared_with=request.user
        ).count()
    except:
        shared_docs = 0


    # =========================
    # 🚀 SEND DATA TO TEMPLATE
    # =========================
    return render(request, 'documents/staff_dashboard.html', {
        'documents': documents,

        # roles
        'is_admin': False,
        'is_staff': True,
        'is_student': False,

        # notifications
        'notifications': notifications,

        # stats (NEW)
        'total_docs': total_docs,
        'my_docs': my_docs,
        'shared_docs': shared_docs,
    })


# ================= STUDENT DASHBOARD =================

@login_required
def student_dashboard(request):
    notifications = Notification.objects.filter(
    user=request.user
    ).order_by('-created_at')[:5]

    if not is_student(request.user):
        return redirect('home')

    documents = Document.objects.filter(
        Q(visibility='public') |
        Q(visibility='student') |
        Q(visibility='shared', shared_with=request.user)
    ).distinct().order_by('-created_at')

    return render(request, 'documents/student_dashboard.html', {
        'documents': documents,
        'is_admin': False,
        'is_staff': False,
        'is_student': True,
        'notifications': notifications,
    })


# ================= ADMIN DASHBOARD =================

@login_required
def admin_dashboard(request):
    notifications = Notification.objects.filter(
    user=request.user
    ).order_by('-created_at')[:5]

    if not request.user.is_superuser:
        return redirect('home')

    search_query = request.GET.get('q')

    documents = Document.objects.all().order_by('-created_at')

    if search_query:
        documents = documents.filter(title__icontains=search_query)

    total_users = User.objects.count()
    total_documents = Document.objects.count()
    total_students = User.objects.filter(groups__name="Student").count()

    monthly_data = (
        Document.objects
        .annotate(month=TruncMonth('created_at'))
        .values('month')
        .annotate(count=Count('id'))
        .order_by('month')
    )

    months = [item['month'].strftime("%b %Y") for item in monthly_data]
    counts = [item['count'] for item in monthly_data]

    return render(request, 'documents/admin_dashboard.html', {
        'total_users': total_users,
        'total_documents': total_documents,
        'total_students': total_students,
        'documents': documents,
        'months': months,
        'counts': counts,
        'is_admin': True,
        'is_staff': False,
        'is_student': False,
        'notifications': notifications,
    })


# ================= SHARE DOCUMENT =================

@login_required
def share_document(request, doc_id):

    if not request.user.is_superuser:
        return JsonResponse({"error": "Unauthorized"}, status=403)

    document = get_object_or_404(Document, id=doc_id)

    if request.method == "POST":

        lecturer_id = request.POST.get("lecturer")
        lecturer = get_object_or_404(User, id=lecturer_id)

        document.shared_with.add(lecturer)

        # ✅ ADD THIS (notify receiver)
        create_notification(lecturer, f"A document '{document.title}' was shared with you")

        # ✅ OPTIONAL (notify admin who shared)
        create_notification(request.user, f"You shared '{document.title}' with {lecturer.username}")

        return JsonResponse({"success": True})

    return JsonResponse({"error": "Invalid request"}, status=400)

# ================= DELETE =================
@login_required
def delete_document(request, doc_id):

    if not request.user.is_superuser:
        return JsonResponse({"error": "Unauthorized"}, status=403)

    document = get_object_or_404(Document, id=doc_id)

    doc_name = document.title   # ✅ capture before delete
    document.delete()

    # ✅ ADD THIS
    create_notification(request.user, f"You deleted '{doc_name}'")

    return JsonResponse({"success": True})


# ================= PROFILE =================

from django.contrib.auth.decorators import login_required

@login_required
def profile(request):

    user = request.user

    context = {
        "user": user,

        # ROLE DETECTION
        "is_admin": user.is_superuser or user.groups.filter(name="Admin").exists(),
        "is_staff": user.groups.filter(name="Staff").exists(),
        "is_student": user.groups.filter(name="Student").exists(),
    }

    return render(request, 'documents/profile.html', context)


# ================= LOGOUT =================

def logout_view(request):

    logout(request)

    messages.success(request, "You have successfully logged out.")

    # ✅ CHANGED: Redirect to landing page instead of login page
    return redirect('landing')


# ================= FETCH NOTIFICATIONS =================

from django.http import JsonResponse

@login_required
def fetch_notifications(request):

    notifications = Notification.objects.filter(
        user=request.user,
        is_read=False
    ).order_by('-created_at')[:5]

    data = []

    for n in notifications:
        data.append({
            "message": n.message
        })

    return JsonResponse({"notifications": data})
from django.http import JsonResponse
from django.db import connection

def health_check(request):
    db_status = "connected"

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
    except Exception as e:
        db_status = f"error: {str(e)}"

    status = {
        "status": "healthy" if db_status == "connected" else "unhealthy",
        "database": db_status,
    }

    return JsonResponse(status)