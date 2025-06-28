from django.core.management.base import BaseCommand
from listings.models import Listing
from django.core.files.base import ContentFile
from io import BytesIO
from PIL import Image
import random
import datetime

class Command(BaseCommand):
    help = 'Seed the database with sample listings'

    def handle(self, *args, **kwargs):
        # Clear existing data
        Listing.objects.all().delete()

        for i in range(5):
            # Create a dummy image
            image = BytesIO()
            img = Image.new('RGB', (100, 100), color=(random.randint(0,255), random.randint(0,255), random.randint(0,255)))
            img.save(image, 'JPEG')
            image.seek(0)
            image_file = ContentFile(image.read(), f'listing_{i}.jpg')

            listing = Listing.objects.create(
                title=f"Sample Listing {i+1}",
                description="This is a sample listing.",
                picture=image_file,
                price_per_night=random.uniform(50, 200),
                available_from=datetime.date.today(),
                available_to=datetime.date.today() + datetime.timedelta(days=30),
            )
            self.stdout.write(self.style.SUCCESS(f'Created listing: {listing.title}'))