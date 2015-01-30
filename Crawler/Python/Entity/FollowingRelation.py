class FollowingRelation:
    def __init__(self):
        print "new FollowingRelation"

    def inflate(self,data):
        fields=data.split(',')
        self.uid=fields[0]
        self.fuid=fields[1]
