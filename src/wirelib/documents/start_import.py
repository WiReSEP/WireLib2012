#!/usr/bin/env python
# vim set fileencoding=utf-8
from documents.models import category
from django.contrib.auth.models import Group, Permission

def importieren():
    #Kategorien
    c = category(name='book')
    c.save()
    c = category(name='unpublished')
    c.save()
    c = category(name='projectwork')
    c.save()
    c = category(name='phdthesis')
    c.save()
    c = category(name='bachelorthesis')
    c.save()
    c = category(name='preamble')
    c.save()
    c = category(name='mastersthesis')
    c.save()

    #Gruppe
    g = Group(id=1, name='Administrator')
    g.save()
    g = Group(id=2, name='UserAdmin')
    g.save()
    g = Group(id=3, name='Bibliothekar')
    g.save()
    g = Group(id=4, name='Mitglieder')
    g.save()
                      
    #group
    Permission.objects.get(id=1).group_set.add(Group.objects.get(id=1))
    Permission.objects.get(id=2).group_set.add(Group.objects.get(id=1))
    Permission.objects.get(id=3).group_set.add(Group.objects.get(id=1))
    Permission.objects.get(id=4).group_set.add(Group.objects.get(id=1))
    Permission.objects.get(id=5).group_set.add(Group.objects.get(id=1))
    Permission.objects.get(id=6).group_set.add(Group.objects.get(id=1))
    Permission.objects.get(id=7).group_set.add(Group.objects.get(id=1))
    Permission.objects.get(id=8).group_set.add(Group.objects.get(id=1))
    Permission.objects.get(id=9).group_set.add(Group.objects.get(id=1))
    Permission.objects.get(id=10).group_set.add(Group.objects.get(id=1))
    Permission.objects.get(id=11).group_set.add(Group.objects.get(id=1))
    Permission.objects.get(id=12).group_set.add(Group.objects.get(id=1))
    Permission.objects.get(id=13).group_set.add(Group.objects.get(id=1))
    Permission.objects.get(id=14).group_set.add(Group.objects.get(id=1))
    Permission.objects.get(id=15).group_set.add(Group.objects.get(id=1))
    Permission.objects.get(id=16).group_set.add(Group.objects.get(id=1))
    Permission.objects.get(id=17).group_set.add(Group.objects.get(id=1))
    Permission.objects.get(id=18).group_set.add(Group.objects.get(id=1))
    Permission.objects.get(id=19).group_set.add(Group.objects.get(id=1))
    Permission.objects.get(id=20).group_set.add(Group.objects.get(id=1))
    Permission.objects.get(id=21).group_set.add(Group.objects.get(id=1))
    Permission.objects.get(id=22).group_set.add(Group.objects.get(id=1))
    Permission.objects.get(id=23).group_set.add(Group.objects.get(id=1))
    Permission.objects.get(id=24).group_set.add(Group.objects.get(id=1))
    Permission.objects.get(id=25).group_set.add(Group.objects.get(id=1))
    Permission.objects.get(id=26).group_set.add(Group.objects.get(id=1))
    Permission.objects.get(id=27).group_set.add(Group.objects.get(id=1))
    Permission.objects.get(id=28).group_set.add(Group.objects.get(id=1))
    Permission.objects.get(id=29).group_set.add(Group.objects.get(id=1))
    Permission.objects.get(id=30).group_set.add(Group.objects.get(id=1))
    Permission.objects.get(id=31).group_set.add(Group.objects.get(id=1))
    Permission.objects.get(id=32).group_set.add(Group.objects.get(id=1))
    Permission.objects.get(id=33).group_set.add(Group.objects.get(id=1))
    Permission.objects.get(id=34).group_set.add(Group.objects.get(id=1))
    Permission.objects.get(id=35).group_set.add(Group.objects.get(id=1))
    Permission.objects.get(id=36).group_set.add(Group.objects.get(id=1))
    Permission.objects.get(id=37).group_set.add(Group.objects.get(id=1))
    Permission.objects.get(id=38).group_set.add(Group.objects.get(id=1))
    Permission.objects.get(id=39).group_set.add(Group.objects.get(id=1))
    Permission.objects.get(id=40).group_set.add(Group.objects.get(id=1))
    Permission.objects.get(id=41).group_set.add(Group.objects.get(id=1))
    Permission.objects.get(id=42).group_set.add(Group.objects.get(id=1))
    Permission.objects.get(id=43).group_set.add(Group.objects.get(id=1))
    Permission.objects.get(id=44).group_set.add(Group.objects.get(id=1))
    Permission.objects.get(id=45).group_set.add(Group.objects.get(id=1))
    Permission.objects.get(id=46).group_set.add(Group.objects.get(id=1))
    Permission.objects.get(id=47).group_set.add(Group.objects.get(id=1))
    Permission.objects.get(id=48).group_set.add(Group.objects.get(id=1))
    Permission.objects.get(id=49).group_set.add(Group.objects.get(id=1))
    Permission.objects.get(id=50).group_set.add(Group.objects.get(id=1))
    Permission.objects.get(id=51).group_set.add(Group.objects.get(id=1))
    Permission.objects.get(id=52).group_set.add(Group.objects.get(id=1))
    Permission.objects.get(id=53).group_set.add(Group.objects.get(id=1))
    Permission.objects.get(id=54).group_set.add(Group.objects.get(id=1))
    Permission.objects.get(id=55).group_set.add(Group.objects.get(id=1))
    Permission.objects.get(id=56).group_set.add(Group.objects.get(id=1))
    Permission.objects.get(id=57).group_set.add(Group.objects.get(id=1))
    Permission.objects.get(id=58).group_set.add(Group.objects.get(id=1))
    Permission.objects.get(id=59).group_set.add(Group.objects.get(id=1))
    Permission.objects.get(id=60).group_set.add(Group.objects.get(id=1))
    Permission.objects.get(id=61).group_set.add(Group.objects.get(id=1))
    Permission.objects.get(id=62).group_set.add(Group.objects.get(id=1))
    Permission.objects.get(id=63).group_set.add(Group.objects.get(id=1))
    Permission.objects.get(id=64).group_set.add(Group.objects.get(id=1))
    Permission.objects.get(id=65).group_set.add(Group.objects.get(id=1))
    Permission.objects.get(id=66).group_set.add(Group.objects.get(id=1))
    Permission.objects.get(id=67).group_set.add(Group.objects.get(id=1))
    Permission.objects.get(id=68).group_set.add(Group.objects.get(id=1))
    Permission.objects.get(id=69).group_set.add(Group.objects.get(id=1))
    Permission.objects.get(id=70).group_set.add(Group.objects.get(id=1))
    
    Permission.objects.get(id=4).group_set.add(Group.objects.get(id=2))
    Permission.objects.get(id=5).group_set.add(Group.objects.get(id=2))
    Permission.objects.get(id=6).group_set.add(Group.objects.get(id=2))
    Permission.objects.get(id=7).group_set.add(Group.objects.get(id=2))
    Permission.objects.get(id=8).group_set.add(Group.objects.get(id=2))
    Permission.objects.get(id=9).group_set.add(Group.objects.get(id=2))
    Permission.objects.get(id=36).group_set.add(Group.objects.get(id=2))
    Permission.objects.get(id=45).group_set.add(Group.objects.get(id=2))
    Permission.objects.get(id=46).group_set.add(Group.objects.get(id=2))
    Permission.objects.get(id=47).group_set.add(Group.objects.get(id=2))
    Permission.objects.get(id=51).group_set.add(Group.objects.get(id=2))
    Permission.objects.get(id=52).group_set.add(Group.objects.get(id=2))
    Permission.objects.get(id=53).group_set.add(Group.objects.get(id=2))
    Permission.objects.get(id=54).group_set.add(Group.objects.get(id=2))
    Permission.objects.get(id=55).group_set.add(Group.objects.get(id=2))
    Permission.objects.get(id=56).group_set.add(Group.objects.get(id=2))
    Permission.objects.get(id=57).group_set.add(Group.objects.get(id=2))
    Permission.objects.get(id=58).group_set.add(Group.objects.get(id=2))
    Permission.objects.get(id=59).group_set.add(Group.objects.get(id=2))
    Permission.objects.get(id=67).group_set.add(Group.objects.get(id=2))
    Permission.objects.get(id=68).group_set.add(Group.objects.get(id=2))
    Permission.objects.get(id=70).group_set.add(Group.objects.get(id=2))
 
    Permission.objects.get(id=7).group_set.add(Group.objects.get(id=3))
    Permission.objects.get(id=23).group_set.add(Group.objects.get(id=3))
    Permission.objects.get(id=25).group_set.add(Group.objects.get(id=3))
    Permission.objects.get(id=26).group_set.add(Group.objects.get(id=3))
    Permission.objects.get(id=27).group_set.add(Group.objects.get(id=3))
    Permission.objects.get(id=28).group_set.add(Group.objects.get(id=3))
    Permission.objects.get(id=29).group_set.add(Group.objects.get(id=3))
    Permission.objects.get(id=31).group_set.add(Group.objects.get(id=3))
    Permission.objects.get(id=32).group_set.add(Group.objects.get(id=3))
    Permission.objects.get(id=34).group_set.add(Group.objects.get(id=3))
    Permission.objects.get(id=35).group_set.add(Group.objects.get(id=3))
    Permission.objects.get(id=36).group_set.add(Group.objects.get(id=3))
    Permission.objects.get(id=37).group_set.add(Group.objects.get(id=3))
    Permission.objects.get(id=38).group_set.add(Group.objects.get(id=3))
    Permission.objects.get(id=39).group_set.add(Group.objects.get(id=3))
    Permission.objects.get(id=40).group_set.add(Group.objects.get(id=3))
    Permission.objects.get(id=41).group_set.add(Group.objects.get(id=3))
    Permission.objects.get(id=42).group_set.add(Group.objects.get(id=3))
    Permission.objects.get(id=43).group_set.add(Group.objects.get(id=3))
    Permission.objects.get(id=44).group_set.add(Group.objects.get(id=3))
    Permission.objects.get(id=45).group_set.add(Group.objects.get(id=3))
    Permission.objects.get(id=49).group_set.add(Group.objects.get(id=3))
    Permission.objects.get(id=50).group_set.add(Group.objects.get(id=3))
    Permission.objects.get(id=51).group_set.add(Group.objects.get(id=3))
    Permission.objects.get(id=54).group_set.add(Group.objects.get(id=3))
    Permission.objects.get(id=55).group_set.add(Group.objects.get(id=3))
    Permission.objects.get(id=57).group_set.add(Group.objects.get(id=3))
    Permission.objects.get(id=58).group_set.add(Group.objects.get(id=3))
    Permission.objects.get(id=59).group_set.add(Group.objects.get(id=3))
    Permission.objects.get(id=60).group_set.add(Group.objects.get(id=3))
    Permission.objects.get(id=61).group_set.add(Group.objects.get(id=3))
    Permission.objects.get(id=63).group_set.add(Group.objects.get(id=3))
    Permission.objects.get(id=64).group_set.add(Group.objects.get(id=3))
    Permission.objects.get(id=65).group_set.add(Group.objects.get(id=3))
    Permission.objects.get(id=66).group_set.add(Group.objects.get(id=3))
    Permission.objects.get(id=70).group_set.add(Group.objects.get(id=3))
    
    Permission.objects.get(id=34).group_set.add(Group.objects.get(id=4))
    Permission.objects.get(id=35).group_set.add(Group.objects.get(id=4))
    Permission.objects.get(id=37).group_set.add(Group.objects.get(id=4))
    Permission.objects.get(id=54).group_set.add(Group.objects.get(id=4))
    Permission.objects.get(id=55).group_set.add(Group.objects.get(id=4))
    Permission.objects.get(id=57).group_set.add(Group.objects.get(id=4))
    Permission.objects.get(id=58).group_set.add(Group.objects.get(id=4))
    Permission.objects.get(id=60).group_set.add(Group.objects.get(id=4))
    Permission.objects.get(id=61).group_set.add(Group.objects.get(id=4))
    Permission.objects.get(id=63).group_set.add(Group.objects.get(id=4))
    Permission.objects.get(id=66).group_set.add(Group.objects.get(id=4))
   