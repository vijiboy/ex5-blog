from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from enum import Enum


# Create your models here.
class Post(models.Model):
    title = models.CharField(max_length=200)
    author = models.ForeignKey("auth.User", on_delete=models.CASCADE)
    body = models.TextField()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("post_detail", kwargs={"pk": self.pk})


class HousingType(models.TextChoices):
    APARTMENT = "apartment"
    STUDIO = "studio"
    FLAT = "flat"
    PLOT = "plot"
    # Add more housing types as needed


class PropertyGroupType(models.TextChoices):
    FLOOR = "floor"
    BUILDING = "building"
    MULTI_STOREY_APARTMENT = "multi-storey-apartment"
    # Add more group types as needed


class PropertyUnit(models.Model):
    """
    Represents a self-contained housing unit within a property.
    """

    # Unique identifier for the unit (e.g., G-607)
    unit_name = models.CharField(max_length=255, unique=True)
    # Type of housing unit (restricted to HousingType enum values)
    housing_type = models.CharField(max_length=255, choices=HousingType.choices)
    # Area of the unit in square feet
    area_sq_ft = models.IntegerField()
    # Foreign key to the Property this unit belongs to
    property = models.ForeignKey("Property", on_delete=models.CASCADE, null=True)
    # Optional image for the unit
    image = models.ImageField(upload_to="property_unit_images/", null=True)

    def save(self, *args, **kwargs):
        """
        Override PropertyUnit.save(), to create new Property if left null for new PropertyUnit
        """
        instance = super().save(*args, **kwargs)
        if not instance.property_id:
            # Create a new Property with the same name and image (if provided)
            new_property = Property.objects.create(
                name=instance.unit_name,
                image=instance.image,
            )
            instance.property = new_property
            instance.save()  # Save the PropertyUnit with the new property
        return instance


class Property(models.Model):
    """
    Represents a property unit or a group of units (building, floor, etc.).
    """

    # Descriptive name for the property (e.g., Floor 3, G-607)
    name = models.CharField(max_length=255)
    # Optional group type (restricted to GroupType enum values)
    group_type = models.CharField(
        max_length=255, choices=PropertyGroupType.choices, blank=True
    )
    # Optional foreign key to another Property for grouping (used for floors/buildings)
    re_group = models.ForeignKey("self", on_delete=models.CASCADE, null=True)
    # Optional additional address information
    address_segment = models.CharField(max_length=255, blank=True)
    # Optional image for the property
    image = models.ImageField(upload_to="property_images/", null=True)


class PropertyOwnership(models.Model):
    """
    Represents ownership of a property by a user on a specific date range.
    Enforces a constraint that a property can only have one owner on a given date.
    """

    # Foreign key to the Property being owned
    property = models.ForeignKey("Property", on_delete=models.CASCADE)
    # Foreign key to the User who owns the property
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # Date ownership starts
    start_date = models.DateField()
    # Optional end date of ownership (defaults to null for ongoing ownership)
    end_date = models.DateField(null=True)

    class Meta:
        unique_together = (("property", "start_date"),)


class RentalLease(models.Model):
    """
    Represents a rental lease agreement for a property between a tenant and owner.
    """

    # Start date of the lease
    start_date = models.DateField()
    # End date of the lease
    stop_date = models.DateField()
    # Foreign key to the Property being leased
    property = models.ForeignKey("Property", on_delete=models.CASCADE)
    # Amount of rent paid per payment cycle
    rent_amount = models.DecimalField(max_digits=10, decimal_places=2)
    # Frequency of rent payments (e.g., monthly, quarterly)
    payment_frequency = models.CharField(max_length=255)
    # Foreign key to the User who is the tenant
    tenant_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="tenant_leases"
    )
    # Foreign key to the User who is the owner
    owner_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="owner_leases"
    )
    # Optional file containing the rental agreement document
    rent_agreement_document = models.FileField(
        upload_to="rental_agreements/", null=True
    )


class Transaction(models.Model):
    """
    Represents a financial transaction related to a property.
    """

    # Date and time the transaction occurred (automatically set on creation)
    datetime = models.DateTimeField(auto_now_add=True)
    # Amount of the transaction (positive or negative)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    # Foreign key to the Property involved in the transaction
    property = models.ForeignKey("Property", on_delete=models.CASCADE)
    # Foreign key to the User receiving funds in the transaction
    to_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="to_transactions"
    )
    # Foreign key to the User initiating the transaction (paying)
    from_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="from_transactions"
    )
    # Optional file containing additional details about the transaction
    transaction_details = models.FileField(
        upload_to="transaction_documents/", null=True
    )
