from typing import TypedDict


class PermitRecord(TypedDict):
    permit_id: str
    address: str
    owner_name: str
    permit_type: str
    permit_subtype: str
    issue_date: str


class PropertyRecord(TypedDict):
    property_id: str
    address: str
    owner_name: str
    mailing_address: str
    owner_occupied: str
    trigger_label: str
    trigger_date: str


class EnrichmentRecord(TypedDict):
    address: str
    owner_name: str
    contact_email: str
    contact_phone: str
    contact_confidence: str


class ScoredLead(TypedDict):
    lead_id: str
    source_type: str
    source_record_id: str
    owner_name: str
    address: str
    address_normalized: str
    trigger_type: str
    trigger_date: str
    contact_email: str
    contact_phone: str
    contact_confidence: str
    owner_occupancy_proxy: str
    score: int
    tier: str
    suggested_opener: str
    score_version: str
    generated_at: str
    export_status: str
