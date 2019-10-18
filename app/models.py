from django.db import models


class DataSource(models.Model):
    date_created = models.DateTimeField(
        auto_now_add=True,
        editable=False,
    )
    name = models.CharField(
        db_index=True,
        max_length=200,
    )


class Campaign(models.Model):
    date_created = models.DateTimeField(
        auto_now_add=True,
        editable=False,
    )
    name = models.CharField(
        db_index=True,
        max_length=200,
    )


class RowData(models.Model):
    date_created = models.DateField(
        auto_now_add=True,
        db_index=True,
        editable=False,
    )
    date = models.DateField()
    data_source = models.ForeignKey(DataSource, on_delete=models.CASCADE)
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    clicks = models.IntegerField()
    impressions = models.IntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    'date', 'data_source', 'campaign', 'clicks', 'impressions'
                ],
                name='unique RowData',
            )
        ]
