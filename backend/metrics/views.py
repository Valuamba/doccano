import abc

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api.models import Example, ExampleState, Project, Annotation, Label, Category, CategoryType, Span, SpanType
from members.models import Member
from members.permissions import IsInProjectReadOnlyOrAdmin


class ProgressAPI(APIView):
    permission_classes = [IsAuthenticated & IsInProjectReadOnlyOrAdmin]

    def get(self, request, *args, **kwargs):
        examples = Example.objects.filter(project=self.kwargs['project_id']).values('id')
        total = examples.count()
        done = ExampleState.objects.count_done(examples, user=self.request.user)
        return {'total': total, 'remaining': total - done}


class MemberProgressAPI(APIView):
    permission_classes = [IsAuthenticated & IsInProjectReadOnlyOrAdmin]

    def get(self, request, *args, **kwargs):
        examples = Example.objects.filter(project=self.kwargs['project_id']).values('id')
        members = Member.objects.filter(project=self.kwargs['project_id'])
        data = ExampleState.objects.measure_member_progress(examples, members)
        return Response(data=data, status=status.HTTP_200_OK)


class LabelDistribution(abc.ABC, APIView):
    permission_classes = [IsAuthenticated & IsInProjectReadOnlyOrAdmin]
    model = Annotation
    label_type = Label

    def get(self, request, *args, **kwargs):
        project = get_object_or_404(Project, pk=self.kwargs['project_id'])
        labels = self.label_type.objects.filter(project=self.kwargs['project_id'])
        examples = Example.objects.filter(project=self.kwargs['project_id']).values('id')
        data = self.model.objects.calc_label_distribution(examples, project.users.all(), labels)
        return Response(data=data, status=status.HTTP_200_OK)


class CategoryTypeDistribution(LabelDistribution):
    model = Category
    label_type = CategoryType


class SpanTypeDistribution(LabelDistribution):
    model = Span
    label_type = SpanType
