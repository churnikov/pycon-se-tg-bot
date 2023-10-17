from tortoise import fields
from tortoise.models import Model


class User(Model):  # type: ignore
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255)
    ticket_id = fields.CharField(max_length=255, null=True)
    is_admin = fields.BooleanField(default=False)


class Room(Model):  # type: ignore
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255)


class Talk(Model):  # type: ignore
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255)
    time_start = fields.DatetimeField()
    time_end = fields.DatetimeField()
    link = fields.CharField(max_length=255, null=True)
    room = fields.ForeignKeyField("models.Room", related_name="talks", null=True)
    speaker = fields.CharField(max_length=255, null=True)
    day = fields.IntField(null=False)


class LikedTalk(Model):  # type: ignore
    talk = fields.ForeignKeyField("models.Talk", related_name="liked_by", on_delete=fields.CASCADE)
    user = fields.ForeignKeyField("models.User", related_name="liked_talks", on_delete=fields.CASCADE)

    class Meta:
        unique_together = (("talk", "user"),)
