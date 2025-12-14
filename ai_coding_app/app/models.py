from django.db import models

#### #! DO NOT MODIFY THIS CODE #! ####

class TestModel(models.Model):
    """
    This is a test model for the app. An example record has been created in the native SQLite database.

    Attributes:
        field1 (str): A string field
        field2 (int): An integer field
    """

    field1 = models.CharField(max_length=100)
    field2 = models.IntegerField()

    def __str__(self) -> str:
        f"""
        Return the string representation of the model instance.

        :return: The string representation of the model instance.
        :rtype: str
        """
        return self.field1
    
    def to_dict(self) -> dict:
        f"""
        Convert the model instance to a dictionary for JSON serialization.

        :return: The dictionary representation of the model instance.
        :rtype: dict
        """
        return {
            'id': self.id,
            'field1': self.field1,
            'field2': self.field2,
        }
    
#### #! END OF DO NOT MODIFY THIS CODE #! ####

# Create your models here.
class MedicalNote(models.Model):
    """
    Model representing a single medical note within a patient chart.

    Each instance corresponds to one note extracted from a medical chart.
    Multiple notes sharing the same chart_id together represent a full chart.

    Attributes:
        chart_id (str): Identifier grouping notes belonging to the same chart.
        note_id (str): Unique identifier for the note from the source document.
        note_type (str): Type/category of the note (e.g., HPI, ROS, ALLERGIES).
        content (str): Free-text clinical content of the note.
        created_at (datetime): Timestamp when the note was created.
    """

    chart_id = models.CharField(
        max_length=100,
        help_text="Identifier grouping notes belonging to the same chart"
    )

    note_id = models.CharField(
        max_length=100,
        unique=True,
        help_text="Unique identifier for the note from the source document"
    )

    note_type = models.CharField(
        max_length=100,
        help_text="Type/category of the note (e.g., HPI, ROS, ALLERGIES)"
    )

    content = models.TextField(
        help_text="Free-text clinical content of the note"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the note was created"
    )

    def __str__(self) -> str:
        """
        Return a readable string representation of the medical note.

        :return: String representation of the note.
        :rtype: str
        """
        return f"{self.chart_id} - {self.note_type} ({self.note_id})"

    def to_dict(self) -> dict:
        """
        Convert the model instance to a dictionary for JSON serialization.

        :return: Dictionary representation of the medical note.
        :rtype: dict
        """
        return {
            "id": self.id,
            "chart_id": self.chart_id,
            "note_id": self.note_id,
            "note_type": self.note_type,
            "content": self.content,
            "created_at": self.created_at.isoformat(),
        }
