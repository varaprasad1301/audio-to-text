# from django.db import models

# # Create your models here.
# from django.db import models

# class Expense(models.Model):
#     description = models.TextField()
#     amount = models.DecimalField(max_digits=10, decimal_places=2)
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"{self.description} - ₹{self.amount}"

# from django.db import models

# class Expense(models.Model):
#     payer = models.CharField(max_length=100)  # Or ForeignKey to a User model
#     description = models.TextField()
#     amount = models.DecimalField(max_digits=10, decimal_places=2)
#     split_with = models.JSONField()  # Store list of names or user IDs
#     split_type = models.CharField(max_length=20, choices=[
#         ('equal', 'Equal'),
#         ('percentage', 'Percentage'),
#         ('custom', 'Custom'),
#     ])
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"{self.payer} paid ₹{self.amount} for {self.description}"

from django.db import models

class Expense(models.Model):
    payer = models.CharField(max_length=100, default="Unknown")
    description = models.TextField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    split_with = models.JSONField(default=list)  # List of user names
    split_type = models.CharField(
        max_length=20,
        choices=[
            ('equal', 'Equal'),
            ('percentage', 'Percentage'),
            ('custom', 'Custom'),
        ],
        default='equal'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.payer} paid ₹{self.amount} for {self.description}"




