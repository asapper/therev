from django.db import models


class Finishing(models.Model):
    # name
    finishing_name = models.CharField(max_length=100)
    # price
    finishing_price = models.DecimalField(max_digits=6, decimal_places=2)
    # quote reference
    # quote = models.ForeignKey(Quote, on_delete=models.CASCADE)

    def __str__(self):
        """Return a string representation of this Finishing."""
        return "{}".format(self.finishing_name)


class Material(models.Model):
    # name
    material_name = models.CharField(max_length=100)
    # price
    material_price = models.DecimalField(max_digits=6, decimal_places=2)
    # quote reference
    # quote = models.ForeignKey(Quote, on_delete=models.CASCADE)

    def __str__(self):
        """Return a string representation of this Material."""
        return "{}".format(self.material_name)


class Paper(models.Model):
    # name
    paper_name = models.CharField(max_length=100)
    # paper width
    paper_width = models.DecimalField(max_digits=4, decimal_places=2)
    # paper length
    paper_length = models.DecimalField(max_digits=4, decimal_places=2)
    # paper price
    paper_price = models.DecimalField(max_digits=5, decimal_places=2)
    # quote reference
    # quote = models.OneToOneField(Quote, on_delete=models.CASCADE)

    def __str__(self):
        """Return a string representation of this Paper."""
        return "{} ({}\" x {}\")".format(
            self.paper_name,
            self.paper_width,
            self.paper_length)
