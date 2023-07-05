import factory

from mapping.enums import ProjectTypes, RuleCorrelations
from mapping.models import (
    MappingCodesystem,
    MappingCodesystemComponent,
    MappingEclPart,
    MappingECLConcept,
    MappingProject,
    MappingTask,
    MappingTaskStatus,
)


class MappingCodesystemFactory(factory.django.DjangoModelFactory):
    """Mapping Codesystem Factory."""

    class Meta:
        model = MappingCodesystem

    codesystem_title = factory.Sequence(lambda n: f"Codesystem #{n}")
    codesystem_version = factory.Sequence(lambda n: 1000 + n)


class MappingCodesystemComponentFactory(factory.django.DjangoModelFactory):
    """Mappign Codesystem Component Factory."""

    class Meta:
        model = MappingCodesystemComponent

    codesystem_id = factory.SubFactory(MappingCodesystemFactory)
    component_id = factory.Sequence(lambda n: f"Component #{n}")


class MappingProjectFactory(factory.django.DjangoModelFactory):
    """Mapping Project Factory."""

    class Meta:
        model = MappingProject

    title = factory.Sequence(lambda n: f"Project #{n}")
    project_type = ProjectTypes.snomed_ecl_to_one.value
    active = True


class MappingTaskStatusFactory(factory.django.DjangoModelFactory):
    """Mapping Task Status Factory."""

    class Meta:
        model = MappingTaskStatus

    project_id = factory.SubFactory(MappingProjectFactory)
    status_title = factory.Sequence(lambda n: f"Status #{n}")
    status_id = factory.Sequence(lambda n: n)
    status_next = factory.Sequence(lambda n: n + 1)


class MappingTaskFactory(factory.django.DjangoModelFactory):
    """Mapping Task Factory."""

    class Meta:
        model = MappingTask

    project_id = factory.SubFactory(MappingProjectFactory)
    category = factory.Sequence(lambda n: f"Category #{n}")
    source_component  = factory.SubFactory(MappingCodesystemComponentFactory)
    status = factory.SubFactory(MappingTaskStatusFactory, project_id=factory.SelfAttribute("..project_id"))


class MappingECLPartFactory(factory.django.DjangoModelFactory):
    """Mapping ECL Part Factory."""

    class Meta:
        model = MappingEclPart


    task = factory.SubFactory(MappingTaskFactory)
    mapcorrelation = RuleCorrelations.exact_match.value


class MappingECLConceptFactory(factory.django.DjangoModelFactory):
    """Mapping ECL Concept Factory."""

    class Meta:
        model = MappingECLConcept

    task = factory.SubFactory(MappingTaskFactory)
    ecl = factory.SubFactory(MappingECLPartFactory, task=factory.SelfAttribute("..task"))
    active = True
