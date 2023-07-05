import enum

class MappingGroups:
    """Collection of Mapping Group Names."""

    project_access = "mapping | access"


class ProjectTypes(enum.Enum):
    """Mapping Project types."""

    one_to_many = '1'
    many_to_one = '2'
    many_to_many = '3'
    snomed_ecl_to_one = '4'

    @classmethod
    def choices(cls):
        return [
            # (code, readable)
            (cls.one_to_many.value, 'One to Many'),
            (cls.many_to_one.value, 'Many to One'),
            (cls.many_to_many.value, 'Many to Many'),
            (cls.snomed_ecl_to_one.value, 'Snomed ECL to one'),
        ]


class RuleCorrelations(enum.Enum):
    """Rule Correlations."""

    broad_to_narrow = '447559001'
    exact_match = '447557004'
    narrow_to_broad = '447558009'
    partial_overlap = '447560006'
    not_mappable = '447556008'
    not_specified = '447561005'

    @classmethod
    def choices(cls):
        return [
            # (code, readable)
            (cls.broad_to_narrow.value, 'Broad to narrow'),
            (cls.exact_match.value, 'Exact match'),
            (cls.narrow_to_broad.value, 'Narrow to broad'),
            (cls.partial_overlap.value, 'Partial overlap'),
            (cls.not_mappable.value, 'Not mappable'),
            (cls.not_specified.value, 'Not specified'),
        ]


class EventActionOptions(enum.Enum):
    status_change = 'status_change'
    user_change = 'user_change'

    @classmethod
    def choices(cls):
        return [
            (cls.status_change.value, 'Status wijzigen'),
            (cls.user_change.value, 'Toegewezen aan gebruiker'),
        ]


class RCStatus(enum.Enum):
    draft = '0'
    active = '1'
    retired = '2'
    unknown = '3'

    @classmethod
    def choices(cls):
        return [
            (RCStatus.draft.value, 'Draft'),
            (RCStatus.active.value, 'Active'),
            (RCStatus.retired.value, 'Retired'),
            (RCStatus.unknown.value, 'Unknown'),
        ]


class AuditTypes(enum.Enum):
    veto = 'AUDIT_VETO'
    advice_error = 'Advice error'
    deprecated_source = 'Deprecated source'
    deprecated_target = 'Deprecated target'
    duplicate_rule = 'ECL - duplicate mapping rule'
    import_type = 'IMPORT'
    maps_to_self = 'Maps to self'
    mismatch_ecl_vs_rules = 'Mismatch ECL vs rules'
    missing_target = 'Missing target'
    priority_error = 'Priority error'
    target_used_in_multiple_tasks = 'Target used in multiple tasks'
    ecl_recursive_exclusion = 'ecl_recursive_exclusion'
    multiple_mapping = 'multiple_mapping'
    nhg_lonic_order = 'nhg_loinc_order_vs_observation'
    empty_query = 'Empty ECL Query'

    @classmethod
    def choices(cls):
        return [
            (AuditTypes.veto, 'AUDIT_VETO'),
            (AuditTypes.advice_error, 'Advice error'),
            (AuditTypes.deprecated_source, 'Deprecated source'),
            (AuditTypes.deprecated_target, 'Deprecated target'),
            (AuditTypes.duplicate_rule, 'ECL - duplicate mapping rule'),
            (AuditTypes.import_type, 'IMPORT'),
            (AuditTypes.maps_to_self, 'Maps to self'),
            (AuditTypes.mismatch_ecl_vs_rules, 'Mismatch ECL vs rules'),
            (AuditTypes.missing_target, 'Missing target'),
            (AuditTypes.priority_error, 'Priority error'),
            (AuditTypes.target_used_in_multiple_tasks, 'Target used in multiple tasks'),
            (AuditTypes.ecl_recursive_exclusion, 'ecl_recursive_exclusion'),
            (AuditTypes.multiple_mapping, 'multiple_mapping'),
            (AuditTypes.nhg_lonic_order, 'nhg_loinc_order_vs_observation'),
            (AuditTypes.empty_query, 'Empty ECL Query')
        ]


class ProjectAuditTypes(enum.Enum):
    unmapped_component = "Concept niet gemapt"

    @classmethod
    def choices(cls):
        return [
            (ProjectAuditTypes.unmapped_component, "Concept niet gemapt")
        ]
