from django.core.management.base import NoArgsCommand

from refugeedata.models import Person


class Command(NoArgsCommand):

    # TODO combine these with the values in models.py
    MAX_WIDTH = 600
    MAX_HEIGHT = 800

    help = ("Scale all Person images that are greater than the maximum size, "
            "and rotate those that need doing so.")

    def add_arguments(self, parser):
        parser.add_argument("--log-on-every", type=int, default=10,
                            help="Log on every X images processed.")

    def _generator(self, people):
        for person in people:
            img = person.photo
            if img.width <= self.MAX_WIDTH and img.height <= self.MAX_HEIGHT:
                self.stdout.write(
                    "Image {} is of an acceptable size.".format(img))
                continue
            try:
                img.open()
                yield img
            finally:
                img.close()

    def handle_noargs(self, **options):
        log_on_every = options.get("log_on_every", 0)
        people_with_images = Person.objects.exclude(photo="")
        self.stdout.write("Found {} people with images".format(
            people_with_images.count()))
        done_count = 0
        for image in self._generator(people_with_images):
            if done_count > 0 and done_count % log_on_every == 0:
                self.stdout.write("Processed {} image(s).".format(done_count))
            image.save(image.name, image.file)  # imagekit does the magic here
            done_count += 1
        self.stdout.write("Processed {} image(s).".format(done_count))
