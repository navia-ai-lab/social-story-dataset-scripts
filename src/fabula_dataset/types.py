from enum import Enum
from typing import Dict, List, Literal, Optional
from pydantic import BaseModel, Field


class GenderEnum(str, Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    PREFER_NOT_TO_SAY = "prefer-not-to-say"


class VerbalAbilityEnum(str, Enum):
    NON_VERBAL = "non-verbal"
    MINIMAL_VERBAL = "minimal-verbal"
    VERBAL = "verbal"
    FLUENT = "fluent"


class FunctionalWordRangeEnum(str, Enum):
    ZERO = "0"
    ONE_TO_TWENTY = "1-20"
    TWENTY_ONE_TO_HUNDRED = "21-100"
    HUNDRED_PLUS = "100+"


CommunicationModalityType = Literal["speech", "aac", "sign", "gestures", "mixed"]
EnvironmentType = Literal[
    "mainstream-school", "special-needs-school", "clinic", "home", "other"
]


class FamilyMember(BaseModel):
    name: str
    relation: str
    hasASD: bool
    preferredLanguage: str
    preferredName: Optional[str] = None


class Caregiver(BaseModel):
    name: str
    role: str
    preferredLanguage: str
    hoursPerWeek: int
    preferredLanguageOther: Optional[str] = None


class LearnerProfile(BaseModel):
    name: str
    age: int
    gender: GenderEnum
    nationality: Optional[str] = None
    primaryLanguage: List[str] = Field(default_factory=list)
    secondaryLanguage: List[str] = Field(default_factory=list)
    familyMembers: List[FamilyMember] = Field(default_factory=list)
    caregivers: List[Caregiver] = Field(default_factory=list)
    verbalAbility: VerbalAbilityEnum
    functionalWordRange: Optional[FunctionalWordRangeEnum] = None
    communicationModality: List[CommunicationModalityType] = Field(default_factory=list)
    sensoryProfile: Dict[str, str] = Field(default_factory=dict)
    sensoryPreferences: Dict[str, str] = Field(default_factory=dict)
    sensoryTriggers: Dict[str, str] = Field(default_factory=dict)
    sensoryNotes: Optional[str] = None
    interests: List[str] = Field(default_factory=list)
    reinforcers: List[str] = Field(default_factory=list)
    preferredFoods: List[str] = Field(default_factory=list)
    preferredActivities: List[str] = Field(default_factory=list)
    primaryEnvironment: List[EnvironmentType] = Field(default_factory=list)
    primaryEnvironmentOther: Optional[str] = Field(default=None, description="If primaryEnvironment is selected to be 'other', state the actual environment here")
    secondaryEnvironment: List[EnvironmentType] = Field(default_factory=list)
    secondaryEnvironmentOther: Optional[str] = Field(default=None, description="If secondaryEnvironment is selected to be 'other', state the actual environment here")
