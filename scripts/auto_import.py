import csv

from hg_app.models import *
from django.contrib.auth.models import User


def point_convert(raw_point):
    point_parts = raw_point.split(',')
    return f"POINT ( {point_parts[1][1:11]} {point_parts[0][:10]} )"



# with open("import_data/names_nicknames.csv") as f:
#     reader2 = csv.reader(f)
#     names_dict = {rows[0]: rows[1] for rows in reader2}


print("uploading packages")
with open("import_data/package_test.csv") as f:
    reader = csv.reader(f)
    for row in reader:
        _, created = Package.objects.get_or_create(
            location=point_convert(row[0]),
            description=row[1],
            opening_time=row[2],
        )
print("packages uploaded")
# print("uploading points")
#
# with open("import_data/point_test.csv") as f:
#     reader = csv.reader(f)
#     for row in reader:
#         _, created = Point.objects.get_or_create(
#             location=point_convert(row[0]),
#             description=row[1],
#             opening_time=row[2],
#             max_number_of_visits=row[3],
#         )
# print("points uploaded")
# print("uploading messages")

#
# with open("import_data/message.csv") as f:
#     reader = csv.reader(f)
#     for row in reader:
#         _, created = Message.objects.get_or_create(
#             text=row[0],
#             brief=row[1],
#             time=row[2],
#         )
#         message = Message.objects.get(text=row[0])
#         for player in row[3:]:
#             message.players.add(Player.objects.get(user=User.objects.get(username=names_dict[player])))
#             message.save()

# print("messages uploaded")
# print("uploading players")

#
# with open("import_data/player.csv") as f:
#     reader = csv.reader(f)
#     for row in reader:
#         player = Player.objects.get(user=User.objects.get(username=names_dict[row[0]]))
#         for point in row[1].split(','):
#             player.points.add(point)
#             player.save()
#
#         for package in row[2].split(','):
#             player.packages.add(package)
#             player.save()
# print("players uploaded")
# print("uploading special actions")
# with open("import_data/special_action.csv") as f:
#     reader = csv.reader(f)
#     for row in reader:
#         SpecialAction.objects.create(
#             effect=row[0],
#         )
# print("special actions uploaded")

