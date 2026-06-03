from django.core.management.base import BaseCommand
from documents.models import Document


class Command(BaseCommand):
    help = (
        'Scan Document.file paths and fix common incorrect prefixes, such as a leading "documents/".'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--apply',
            action='store_true',
            help='Actually update the database records. Without this flag the command only reports proposed changes.',
        )
        parser.add_argument(
            '--prefix',
            default='documents/',
            help='The prefix to remove from stored file paths. Defaults to "documents/".',
        )
        parser.add_argument(
            '--only-if',
            default='',
            help='Only consider file paths containing this substring.',
        )

    def handle(self, *args, **options):
        prefix = options['prefix']
        only_if = options['only_if']
        apply_changes = options['apply']

        documents = Document.objects.all()
        fixes = []

        for doc in documents:
            path = doc.file.name
            if only_if and only_if not in path:
                continue

            new_path = path
            while new_path.startswith(prefix):
                new_path = new_path[len(prefix):]

            if new_path != path:
                fixes.append((doc, path, new_path))

        if not fixes:
            self.stdout.write(self.style.SUCCESS('No file paths require fixing.'))
            return

        self.stdout.write(self.style.WARNING(f'Found {len(fixes)} document(s) with paths starting with "{prefix}".'))

        for doc, old_path, new_path in fixes:
            self.stdout.write(f'  id={doc.id} title="{doc.title}"\n    {old_path} -> {new_path}')

        if apply_changes:
            for doc, old_path, new_path in fixes:
                doc.file.name = new_path
                doc.save(update_fields=['file'])
            self.stdout.write(self.style.SUCCESS(f'Updated {len(fixes)} document(s).'))
        else:
            self.stdout.write(self.style.NOTICE('Run with --apply to persist these changes.'))
