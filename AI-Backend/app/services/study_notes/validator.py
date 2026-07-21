from app.domain.schemas.study_notes import StudyNotesRequest, NoteType
from app.core.exceptions import StudyNotesValidationError

class StudyNotesValidator:
    """
    Validates input requests for the Study Notes Generator.
    """
    
    @staticmethod
    def validate_request(request: StudyNotesRequest) -> None:
        """
        Validates the incoming study notes request.
        """
        if not request.topic or not request.topic.strip():
            raise StudyNotesValidationError("Topic cannot be empty")
            
        if request.creativity < 0.0 or request.creativity > 1.0:
            raise StudyNotesValidationError("Creativity must be between 0.0 and 1.0")
            
        if request.length_words < 100 or request.length_words > 4000:
            raise StudyNotesValidationError("Notes length must be between 100 and 4000 words")
            
        if request.note_type not in [m.value for m in NoteType]:
            raise StudyNotesValidationError(f"Invalid note type: {request.note_type}")
