from django.db import models
from django.db.models import F, Q, Count, Case, When
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

# 1. Model mixins
# Advantages: Allows you to reuse code by adding methods or properties
#             to multiple models without inheritance.
class TimestampMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class Author(TimestampMixin):
    name = models.CharField(max_length=100)

# 2. Model signals
# Advantages: Allows you to perform actions in response to changes in the model
#             lifecycle, such as validating, modifying, or tracking changes.
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField()

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

# 3. Model managers
# Advantages: Provides a centralized way to define custom query methods for your
#             models, making it easy to reuse and maintain your code.
class ActiveProductManager(models.Manager):
    def active(self):
        return self.filter(is_active=True)

class Product(models.Model):
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    objects = ActiveProductManager()

# 4. Conditional expressions
# Advantages: Allows you to perform complex, database-backed conditional operations
#             directly in your queries, reducing the need for Python-side processing.
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total = models.DecimalField(max_digits=10, decimal_places=2)

Order.objects.annotate(
    discount=Case(
        When(total__gt=100, then=F('total') * 0.1),
        default=0,
        output_field=models.DecimalField(),
    )
)

# 5. Query expressions
# Advantages: Provides a powerful way to construct complex queries, leveraging
#             the full power of your database's query engine.
books = Book.objects.annotate(
    num_authors=Count('authors')
).filter(
    Q(num_authors__gt=1) | Q(title__icontains='Django')
)

# 6. Migrations with RunPython
# Advantages: Allows you to execute custom Python code during migrations,
#             providing a way to handle complex schema changes and data migrations.
from django.db import migrations

def do_something(apps, schema_editor):
    Product = apps.get_model('myapp', 'Product')
    for product in Product.objects.all():
        product.name = product.name.upper()
        product.save()

class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(do_something),
    ]



from django.db import models
from django.contrib.auth.models import User

# 7. Proxy models
# Advantages: Allows you to extend a model without creating a new database table,
#             which makes it easy to add model methods and properties.
class EmployeeManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_employee=True)

class Employee(User):
    class Meta:
        proxy = True
    objects = EmployeeManager()

# 8. Multi-table inheritance
# Advantages: Allows you to create a model that inherits from another model,
#             creating a new table for the child model, and allowing you to add
#             additional fields.
class Person(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)

class Employee(Person):
    employee_id = models.CharField(max_length=10)

# 9. Abstract base classes
# Advantages: Allows you to create a base class that can be inherited by other
#             models, without creating a table for the base class. This enables
#             code reuse and a DRY (Don't Repeat Yourself) approach.
class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class Customer(BaseModel):
    name = models.CharField(max_length=100)

# 10. Database index optimization
# Advantages: Adding a database index improves the query performance on specific
#             fields. It is particularly helpful for fields that are often used in
#             filtering, ordering, or searching.
class Product(models.Model):
    name = models.CharField(max_length=100, db_index=True)
    price = models.DecimalField(max_digits=5, decimal_places=2)
    description = models.TextField()

    class Meta:
        indexes = [
            models.Index(fields=['name'], name='name_idx'),
        ]




# Squashing migrations
# Description: Combines several migration files into one, reducing the number of migration files to maintain and apply.
# Usage: Run the following command, replacing <app_name> with the name of your app and <start_migration> and <end_migration> with the range of migration names to squash.

python manage.py squashmigrations <app_name> <start_migration> <end_migration>


# Data migrations
# Description: Migrate data between different schema versions, such as copying data from one table to another or transforming data.
# Example:


from django.db import migrations, models

def copy_data(apps, schema_editor):
    OldModel = apps.get_model('myapp', 'OldModel')
    NewModel = apps.get_model('myapp', 'NewModel')
    for old_model in OldModel.objects.all():
        NewModel.objects.create(name=old_model.name)

class Migration(migrations.Migration):
    dependencies = [
        ('myapp', '0002_auto_create_new_model'),
    ]
    operations = [
        migrations.RunPython(copy_data),
    ]
# Reversible RunPython operations
# Description: Add a reverse operation for a RunPython migration, allowing the migration to be rolled back.
# Example:

from django.db import migrations

def do_something(apps, schema_editor):
    # forward operation

def undo_something(apps, schema_editor):
    # reverse operation

class Migration(migrations.Migration):
    dependencies = [
        ('myapp', '0001_initial'),
    ]
    operations = [
        migrations.RunPython(do_something, reverse_code=undo_something),
    ]


# Custom migration operations
# Description: Create your own migration operation for complex or application-specific tasks.
# Example:

from django.db import migrations

class CustomOperation(migrations.Operation):
    reversible = True

    def state_forwards(self, app_label, state):
        # state-related changes

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        # forward operation

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        # reverse operation

class Migration(migrations.Migration):
    dependencies = [
        ('myapp', '0001_initial'),
    ]
    operations = [
        CustomOperation(),
    ]


# Dependency management
# Description: Use dependencies to manage the order in which migrations are applied, ensuring proper database state.
# Example:

class Migration(migrations.Migration):
    dependencies = [
        ('myapp', '0001_initial'),
        ('another_app', '0002_add_field'),
    ]
    operations = [
        # ...
    ]


# Handling merge conflicts
# Description: Resolve migration conflicts caused by concurrent development or merging branches.
# Solution:

Identify the conflicting migrations.
Modify the dependencies of the conflicting migration to create a linear migration history.
