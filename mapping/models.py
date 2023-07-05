from datetime import datetime

from django.contrib.auth.models import User
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.utils import timezone

from app.model_fields import ArrayField
from mapping.enums import EventActionOptions, ProjectTypes, RCStatus, RuleCorrelations


class MappingCodesystem(models.Model):
    """Mapping Codesystems."""

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["id"], name="Unique ID"),
        ]

    codesystem_title = models.CharField(max_length=500)
    codesystem_version = models.CharField(max_length=500)
    codesystem_fhir_uri = models.CharField(
        max_length=500, default=None, null=True, blank=True
    )
    component_fhir_uri = models.CharField(
        max_length=500, default=None, null=True, blank=True
    )
    component_created = models.DateTimeField(default=timezone.now)

    # extra fields are legacy, older scripts will break by removing
    codesystem_extra_1 = models.CharField(
        max_length=500, default=None, null=True, blank=True
    )
    codesystem_extra_2 = models.CharField(
        max_length=500, default=None, null=True, blank=True
    )
    codesystem_extra_3 = models.CharField(
        max_length=500, default=None, null=True, blank=True
    )
    codesystem_extra_4 = models.CharField(
        max_length=500, default=None, null=True, blank=True
    )
    codesystem_extra_5 = models.CharField(
        max_length=500, default=None, null=True, blank=True
    )
    codesystem_extra_6 = models.CharField(
        max_length=500, default=None, null=True, blank=True
    )
    codesystem_extra_7 = models.CharField(
        max_length=500, default=None, null=True, blank=True
    )

    objects = models.Manager()

    def __str__(self):
        return f"{self.id} {self.codesystem_title} {self.codesystem_version}"


class MappingCodesystemComponent(models.Model):
    """Mapping Codesystem Component."""

    class Meta:
        indexes = [
            models.Index(fields=["codesystem_id"]),
            models.Index(fields=["component_id"]),
        ]

    # codesystem_id       = models.CharField(max_length=50)
    codesystem_id = models.ForeignKey("MappingCodesystem", on_delete=models.PROTECT)
    component_id = models.CharField(max_length=50)
    component_title = models.CharField(max_length=500)
    component_created = models.DateTimeField(default=timezone.now)
    descriptions = models.JSONField(default=None, null=True, blank=True)
    component_extra_dict = models.JSONField(default=None, null=True, blank=True)
    parents = models.TextField(default=None, null=True, blank=True)
    children = models.TextField(default=None, null=True, blank=True)
    descendants = models.TextField(default=None, null=True, blank=True)
    ancestors = models.TextField(default=None, null=True, blank=True)

    # extra fields are legacy, older scripts will break by removing
    component_extra_5 = models.CharField(
        max_length=500, default=None, null=True, blank=True
    )
    component_extra_6 = models.CharField(
        max_length=500, default=None, null=True, blank=True
    )
    component_extra_7 = models.CharField(
        max_length=500, default=None, null=True, blank=True
    )

    objects = models.Manager()

    def __str__(self):
        return " - ".join(
            [
                str(self.id),
                str(self.codesystem_id.codesystem_title),
                self.component_id,
                self.component_title,
            ]
        )


class MappingProject(models.Model):
    """Base Mapping Project model."""

    title = models.CharField(max_length=300)
    created = models.DateTimeField(default=timezone.now)
    project_type = models.CharField(
        max_length=50,
        choices=ProjectTypes.choices(),
        default=None,
        blank=True,
        null=True,
    )

    categories = models.JSONField(default=list, null=True, blank=True)
    tags = models.JSONField(default=None, null=True, blank=True)

    use_mapgroup = models.BooleanField(blank=True, null=True, default=False)
    use_mappriority = models.BooleanField(blank=True, null=True, default=False)
    use_mapcorrelation = models.BooleanField(blank=True, null=True, default=False)
    use_mapadvice = models.BooleanField(blank=True, null=True, default=False)
    use_maprule = models.BooleanField(blank=True, null=True, default=False)
    use_rulebinding = models.BooleanField(blank=True, null=True, default=False)

    automap_valueset = models.CharField(
        max_length=500, default=None, blank=True, null=True
    )
    automap_method = models.CharField(
        max_length=50, default="MML", blank=True, null=True
    )
    ecl_scope = models.TextField(default=None, blank=True, null=True)

    status_complete = models.ForeignKey(
        "MappingTaskStatus",
        related_name="status_complete",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        default=None,
    )
    status_rejected = models.ForeignKey(
        "MappingTaskStatus",
        related_name="status_rejected",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        default=None,
    )
    access = models.ManyToManyField(
        User, related_name="access_users", default=None, blank=True
    )

    source_codesystem = models.ForeignKey(
        MappingCodesystem,
        on_delete=models.PROTECT,
        related_name="project_source",
        default=None,
        blank=True,
        null=True,
    )
    target_codesystem = models.ForeignKey(
        MappingCodesystem,
        on_delete=models.PROTECT,
        related_name="project_target",
        default=None,
        blank=True,
        null=True,
    )

    active = models.BooleanField(default=True)

    objects = models.Manager()

    def __str__(self):
        return str(self.id) + " " + str(self.title)


class MappingTaskStatus(models.Model):
    """Mapping Task Status."""

    project_id = models.ForeignKey(MappingProject, on_delete=models.PROTECT)
    status_title = models.CharField(
        max_length=50
    )  # Uniek ID in codesystem = MappingCodesystemComponent:id
    status_id = (
        models.IntegerField()
    )  # Uniek ID van codesystem waar vandaan in deze taak gemapt moet worden
    status_description = models.TextField(
        default=None, blank=True, null=True
    )  # Uniek ID van codesystem waar naartoe in deze taak gemapt moet worden
    status_next = models.CharField(max_length=50)  # ID van gebruiker

    objects = models.Manager()

    def __str__(self):
        return (
            f"{self.id} "
            f"Status ID: {self.status_id} "
            f"@ project {self.project_id}: {self.status_title}"
        )


class MappingTask(models.Model):
    """Mapping tasks."""

    project_id = models.ForeignKey(
        MappingProject, on_delete=models.PROTECT, related_name="tasks"
    )
    category = models.CharField(max_length=500)
    # Uniek ID in codesystem = MappingCodesystemComponent:id
    source_component = models.ForeignKey(
        MappingCodesystemComponent, on_delete=models.PROTECT
    )
    # Uniek ID van codesystem waar vandaan in deze taak gemapt moet worden
    source_codesystem = models.ForeignKey(
        MappingCodesystem,
        on_delete=models.PROTECT,
        related_name="source_codesystem_task",
        default=None,
        null=True,
        blank=True,
    )
    # Uniek ID van codesystem waar naartoe in deze taak gemapt moet worden
    target_codesystem = models.ForeignKey(
        MappingCodesystem,
        on_delete=models.PROTECT,
        related_name="target_codesystem_task",
        default=None,
        null=True,
        blank=True,
    )
    # Exclusions
    exclusions = ArrayField(models.CharField(max_length=20), null=True, blank=True)
    # ID van gebruiker
    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        default=None,
        null=True,
        blank=True,
        related_name="tasks",
    )
    # ID van status
    status = models.ForeignKey(
        MappingTaskStatus, on_delete=models.PROTECT, default=None, null=True, blank=True
    )
    task_created = models.DateTimeField(default=timezone.now)

    objects = models.Manager()

    def __str__(self):
        return "Taak ID {}: {} * source component {}".format(
            self.id,
            self.project_id,
            self.source_component,
        )


class MappingComment(models.Model):
    """User comments for Mapping Tasks."""

    comment_title = models.CharField(max_length=50, default=None, null=True, blank=True)
    comment_task = models.ForeignKey(MappingTask, on_delete=models.PROTECT)
    comment_body = models.TextField(max_length=500, default=None, null=True, blank=True)
    # comment_user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment_user = models.ForeignKey(User, on_delete=models.PROTECT)
    comment_created = models.DateTimeField(default=timezone.now)

    objects = models.Manager()

    def __str__(self):
        return f"{self.id} {self.comment_task.id} {self.comment_user.username}"


class MappingRule(models.Model):
    """Mapping Rule details."""

    id = models.BigAutoField(primary_key=True)
    project_id = models.ForeignKey(MappingProject, on_delete=models.PROTECT)
    # Component ID in source codesystem = MappingCodesystems:component_id
    source_component = models.ForeignKey(
        MappingCodesystemComponent,
        on_delete=models.PROTECT,
        related_name="source_component_rule",
    )
    # Uniek ID van codesystem waar naartoe in deze taak gemapt moet worden
    target_component = models.ForeignKey(
        MappingCodesystemComponent,
        on_delete=models.PROTECT,
        related_name="target_component_rule",
    )
    mapgroup = models.IntegerField(default=None, blank=True, null=True)
    mappriority = models.IntegerField(default=None, blank=True, null=True)
    mapcorrelation = models.CharField(
        max_length=50,
        choices=RuleCorrelations.choices(),
        default=None,
        blank=True,
        null=True,
    )
    mapadvice = models.CharField(max_length=500, default=None, blank=True, null=True)
    maprule = models.CharField(max_length=500, default=None, blank=True, null=True)
    mapspecifies = models.ManyToManyField("MappingRule")

    active = models.BooleanField(max_length=50, null=True)  # Actief of deprecated rule

    objects = models.Manager()


class MappingEclPart(models.Model):
    """Mapping ECL Part.

    For use with the vue mapping tooling
    Used to create groups of ECL queries, with their own separate correlation options
    """

    task = models.ForeignKey(MappingTask, on_delete=models.PROTECT)
    query = models.TextField(default=None, blank=True, null=True)
    mapcorrelation = models.CharField(
        max_length=50,
        choices=RuleCorrelations.choices(),
        default=None,
        blank=True,
        null=True,
    )
    description = models.TextField(default=None, blank=True, null=True)

    error = models.TextField(default=None, blank=True, null=True)
    result = models.JSONField(
        encoder=DjangoJSONEncoder, default=dict, blank=True, null=True
    )

    # Export to mapping rules finished?
    export_finished = models.BooleanField(default=True)
    # Retrieved result of query from Snowstorm?
    finished = models.BooleanField(default=False)
    # Query or export failed?2
    failed = models.BooleanField(default=False)

    objects = models.Manager()


class MappingECLConcept(models.Model):
    """Mapping ECL Part Result entity.

    Used to store ECL query result data.
    """

    ecl = models.ForeignKey(
        MappingEclPart, related_name="concepts", on_delete=models.CASCADE
    )
    task = models.ForeignKey(
        MappingTask, related_name="concepts", on_delete=models.CASCADE
    )
    code = models.CharField(max_length=50)
    module_id = models.CharField(max_length=255)
    effective_time = models.DateField(blank=True, null=True)
    definition_status = models.CharField(max_length=15)
    id_and_fsn_term = models.TextField()
    active = models.BooleanField()
    preferred_title = models.TextField()
    pt_lang = models.CharField(max_length=2)
    fsn = models.TextField()
    fsn_lang = models.CharField(max_length=2)
    is_new = models.BooleanField(null=True)
    is_deleted = models.BooleanField(null=True)

    objects = models.Manager()

    @classmethod
    def from_part_result(cls, ecl_part: MappingEclPart, result: dict):
        """Create MappingECLConcept instance from MappingECLPart and it's result."""
        concept_date = None
        if result["effectiveTime"]:
            concept_date = datetime.strptime(result["effectiveTime"], "%Y%m%d")
        return cls(
            ecl=ecl_part,
            task_id=ecl_part.task_id,
            code=result["conceptId"],
            module_id=result["moduleId"],
            effective_time=concept_date,
            definition_status=result["definitionStatus"],
            id_and_fsn_term=result["idAndFsnTerm"],
            active=result["active"],
            preferred_title=result["pt"]["term"],
            pt_lang=result["pt"]["lang"],
            fsn=result["fsn"]["term"],
            fsn_lang=result["fsn"]["lang"],
            is_new=True,
        )


class MappingEclPartExclusion(models.Model):
    """
    Mapping ECL Part Exclusions.

    For use with the vue mapping tooling
    Used to exclude the result of the ECL mapping of another component.
    Ie. putting A80 in the list in MappingEclPartExclusion.components
    will exclude the results of all ECL queries linked to A80 for the linked task.
    """

    task = models.ForeignKey(MappingTask, on_delete=models.PROTECT)
    components = models.JSONField(
        encoder=DjangoJSONEncoder, default=list, blank=True, null=True
    )

    objects = models.Manager()


class MappingEventLog(models.Model):
    """Mapping Event Log entry."""

    task = models.ForeignKey(MappingTask, on_delete=models.PROTECT)
    action = models.CharField(
        max_length=500, choices=EventActionOptions.choices()
    )  # Beschrijving van actie (status_update)
    action_description = models.CharField(
        max_length=500
    )  # Leesbare beschrijving van actie (Status gewijzigd)
    action_user = models.ForeignKey(  # Huidige gebruiker
        User,
        on_delete=models.PROTECT,
        related_name="event_action_user",
        default=None,
        blank=True,
        null=True,
    )
    old_data = models.TextField()  # Oude situatie - payload
    new_data = models.TextField()  # Nieuwe situatie - payload
    old = models.TextField()  # Oude situatie - leesbaar
    new = models.TextField()  # Nieuwe situatie - leesbaar
    user_source = models.ForeignKey(  # Huidige gebruiker
        User, on_delete=models.PROTECT, related_name="user_event_source"
    )
    user_target = (
        models.ForeignKey(  # Gebruiker waaraan gerefereerd wordt, niet verplicht
            User,
            on_delete=models.PROTECT,
            related_name="user_event_target",
            default=None,
            blank=True,
            null=True,
        )
    )
    event_time = models.DateTimeField(default=timezone.now)

    objects = models.Manager()

    def __str__(self):
        return f"{self.id} Task ID: {self.task.id} Actie: {self.action_description}"


class MappingProgressRecord(models.Model):
    """Mapping Progress Records."""

    name = models.TextField()
    project = models.ForeignKey(MappingProject, on_delete=models.PROTECT)
    labels = models.TextField()
    values = models.TextField()
    time = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.id} {self.project} {self.name}"


class MappingProjectAudit(models.Model):
    """Mapping Project Audit Record."""

    audit_type = models.TextField()
    project = models.ForeignKey(MappingProject, on_delete=models.PROTECT)
    extra_1 = models.CharField(max_length=255, default=None, blank=True, null=True)
    extra_2 = models.CharField(max_length=255, default=None, blank=True, null=True)
    hit_reason = models.TextField(default=None, blank=True, null=True)
    comment = models.TextField(default=None, blank=True, null=True)
    ignore = models.BooleanField(default=False)  # Whitelist
    ignore_user = models.ForeignKey(  # User adding the whitelist
        User, default=None, blank=True, null=True, on_delete=models.PROTECT
    )
    first_hit_time = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.project} {self.id} {self.audit_type}"


class MappingTaskAudit(models.Model):
    """Mapping Taks Audit Record."""

    audit_type = models.TextField()
    task = models.ForeignKey(MappingTask, on_delete=models.PROTECT)
    hit_reason = models.TextField(default=None, blank=True, null=True)
    comment = models.TextField(default=None, blank=True, null=True)
    ignore = models.BooleanField(default=False)  # Whitelist
    sticky = models.BooleanField(
        default=False
    )  # True = will not be removed with each audit cycle
    ignore_user = models.ForeignKey(  # User adding the whitelist
        User, default=None, blank=True, null=True, on_delete=models.PROTECT
    )
    first_hit_time = models.DateTimeField(default=timezone.now)


class MappingReleaseCandidate(models.Model):
    """Mapping RC."""

    title = models.TextField(default=None, blank=True, null=True)

    metadata_id = models.TextField(default=None, blank=True, null=True)
    metadata_url = models.TextField(default=None, blank=True, null=True)
    metadata_description = models.TextField(default=None, blank=True, null=True)
    metadata_version = models.TextField(default=None, blank=True, null=True)
    metadata_experimental = models.BooleanField(default=True)
    metadata_date = models.TextField(default=None, blank=True, null=True)
    metadata_publisher = models.TextField(default=None, blank=True, null=True)
    metadata_contact = models.TextField(default=None, blank=True, null=True)
    metadata_copyright = models.TextField(default=None, blank=True, null=True)
    metadata_sourceUri = models.TextField(default=None, blank=True, null=True)
    # Projects to include in export
    export_project = models.ManyToManyField(
        MappingProject, related_name="project", blank=True
    )
    # Who has access to the RC
    access = models.ManyToManyField(
        User, related_name="access_rc_users", default=None, blank=True
    )
    # Source codesystem
    codesystem = models.ForeignKey(
        MappingCodesystem,
        on_delete=models.PROTECT,
        related_name="rc_source_codesystem",
        default=None,
        blank=True,
        null=True,
    )
    # [Optional] Target codesystem - to allow filtering
    target_codesystem = models.ForeignKey(
        MappingCodesystem,
        on_delete=models.PROTECT,
        related_name="rc_target_codesystem",
        default=None,
        blank=True,
        null=True,
    )

    # If True: export ALL rules, regardless of fiat/veto
    export_all = models.BooleanField(default=False)
    # If True: export ALL tasks, regardless of task status
    import_all = models.BooleanField(default=False)
    # Status of exporet
    finished = models.BooleanField(default=False)
    # Perhaps status should be coming from the status DB table - text for now
    status = models.CharField(
        default=None, max_length=50, blank=True, null=True, choices=RCStatus.choices()
    )
    created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return str(self.title)


class MappingReleaseCandidateFHIRConceptMap(models.Model):
    """Mapping RC FHIR Concept Map."""

    title = models.TextField(default=None, blank=True, null=True)
    release_notes = models.TextField(default=None, blank=True, null=True)

    rc = models.ForeignKey(
        MappingReleaseCandidate,
        on_delete=models.PROTECT,
        default=None,
        blank=True,
        null=True,
    )
    # Source codesystem
    codesystem = models.ForeignKey(
        MappingCodesystem,
        on_delete=models.PROTECT,
        related_name="source_codesystem_for_rc",
        default=None,
        blank=True,
        null=True,
    )
    created = models.DateTimeField(default=timezone.now)
    deprecated = models.BooleanField(default=False)
    data = models.JSONField(encoder=DjangoJSONEncoder)


class MappingReleaseCandidateRules(models.Model):
    """Mapping RC Rules."""

    # Contains the individual rules to be included in the MappingReleaseCandidate
    export_rc = models.ForeignKey(
        MappingReleaseCandidate,
        on_delete=models.PROTECT,
        default=None,
        null=True,
        blank=True,
    )
    # Export data
    export_date = models.DateTimeField(default=timezone.now)
    export_user = models.ForeignKey(
        User, on_delete=models.PROTECT, default=None, null=True, blank=True
    )
    # Foreign key bound task used for export
    export_task = models.ForeignKey(
        MappingTask, on_delete=models.SET_NULL, default=None, blank=True, null=True
    )
    # Foreign key bound rule used for export
    export_rule = models.ForeignKey(
        MappingRule, on_delete=models.SET_NULL, default=None, blank=True, null=True
    )
    # Denormalized task data
    task_status = models.TextField(default=None, blank=True, null=True)
    task_user = models.TextField(default=None, blank=True, null=True)
    # Denormalized source component
    source_component = models.ForeignKey(
        MappingCodesystemComponent,
        on_delete=models.SET_NULL,
        related_name="source_component",
        default=None,
        blank=True,
        null=True,
    )
    static_source_component_ident = models.CharField(
        max_length=50, default=None, blank=True, null=True
    )
    static_source_component = models.JSONField(default=None, null=True, blank=True)
    # Denormalized target component
    target_component = models.ForeignKey(
        MappingCodesystemComponent,
        on_delete=models.SET_NULL,
        related_name="target_component",
        default=None,
        blank=True,
        null=True,
    )
    static_target_component_ident = models.CharField(
        max_length=50, default=None, blank=True, null=True
    )
    static_target_component = models.JSONField(default=None, null=True, blank=True)
    # Denormalized rule components
    mapgroup = models.IntegerField(default=None, blank=True, null=True)
    mappriority = models.IntegerField(default=None, blank=True, null=True)
    mapcorrelation = models.CharField(
        max_length=50,
        choices=RuleCorrelations.choices(),
        default=None,
        blank=True,
        null=True,
    )
    mapadvice = models.CharField(max_length=500, default=None, blank=True, null=True)
    maprule = models.CharField(max_length=500, default=None, blank=True, null=True)
    # Denormalized rule bindings
    mapspecifies = models.JSONField(default=None, null=True, blank=True)
    # Log accepted
    accepted = ArrayField(models.IntegerField(), null=True, blank=True)
    # Log rejected
    rejected = ArrayField(models.IntegerField(), null=True, blank=True)

    def __str__(self):
        return str(self.export_task)
