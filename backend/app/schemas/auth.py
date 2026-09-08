from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator


class LoginRequest(BaseModel):
    """Login credentials.

    ``identifier`` is the primary, intended login value: an institutional
    identifier such as ``STU-0012``, ``TCH-0004``, or ``ADM-0001``. ``email``
    is kept as a deprecated backward-compatible alias (existing internal
    callers/tests still send ``email``) and is only used when ``identifier``
    is not supplied.
    """

    identifier: str | None = Field(default=None, min_length=1)
    email: EmailStr | None = None
    password: str

    @field_validator("identifier", mode="before")
    @classmethod
    def _trim_identifier(cls, value):
        if value is None:
            return None
        if isinstance(value, str):
            value = value.strip()
            return value or None
        return value

    @model_validator(mode="after")
    def require_identifier_or_email(self):
        if not self.identifier and not self.email:
            raise ValueError("identifier is required")
        return self

    @property
    def login_value(self) -> str:
        """The raw value to resolve to a User: the institutional identifier
        if provided, otherwise the legacy email alias."""
        return self.identifier if self.identifier else self.email


class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str