from connector import Mongo


class Muscle:
    def __init__(self, name, action_list, relative_muscle, muscle_group):
        self.name = name
        self.action_list = action_list
        self.relative_muscle = relative_muscle
        self.muscle_group = muscle_group

    def get_action(self, require):
        ret = []
        for action in self.action_list:
            if action.match(require):
                ret += action
        return ret



class MuscleGroup:
    def __init__(self, name):
        self.name = name

    def list_muscleGroup_action(self):
        res = Mongo.muscle.find_one({'name': self.name})
        dict_muscle = res['muscleGroup']
        new_dict = str(dict_muscle).replace(' ','').split(',')
        return new_dict

    def find_related_action(self):
        res = Mongo.action.find()
        action_list = []
        str_list = []
        count = 0
        for i in res:
            if i['mainMuscle'] == self.name:
                if count <= 4:
                    str_list.append(i['name'])
                if i['mainMuscle'] not in action_list:
                    action_list.append(i['name'])
                count += 1
        str_list =str(str_list).replace('[','').replace(']','').replace('\'','')
        return str_list,action_list

    def find_related_equipments(self):
        res = Mongo.action.find()
        str_list = []
        equipment_list = []
        count = 0
        for i in res:
            if i['mainMuscle'] == self.name:
                if count <= 4:
                    str_list.append(i['equipment'])
                if i['equipment'] not in equipment_list:
                    equipment_list.append(i['equipment'])
        str_list = str(str_list).replace('[','').replace(']','').replace('\'','')
        return str_list,equipment_list

