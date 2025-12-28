# Generated manually to handle ManyToManyField with through model

from django.db import migrations, models
import django.db.models.deletion
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0001_initial'),
        ('assessments', '0001_initial'),
    ]

    operations = [
        # Step 1: Create the through model first
        migrations.CreateModel(
            name='AssessmentLOContribution',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('contribution_percentage', models.DecimalField(decimal_places=2, help_text='Percentage contribution of this assessment to this LO (0-100)', max_digits=5, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)])),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('assessment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lo_contributions', to='assessments.assessment')),
                ('learning_outcome', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assessment_contributions', to='courses.learningoutcome')),
            ],
            options={
                'ordering': ['assessment', 'learning_outcome'],
                'unique_together': {('assessment', 'learning_outcome')},
            },
        ),
        # Step 2: Remove the old ManyToManyField
        migrations.RemoveField(
            model_name='assessment',
            name='covered_LOs',
        ),
        # Step 3: Add the new ManyToManyField with through model
        migrations.AddField(
            model_name='assessment',
            name='covered_LOs',
            field=models.ManyToManyField(blank=True, help_text='Learning Outcomes covered by this assessment with contribution percentages', related_name='assessments', through='assessments.AssessmentLOContribution', to='courses.learningoutcome'),
        ),
    ]

