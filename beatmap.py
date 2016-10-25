from enum import Enum
from datetime import datetime
import decimal

class HitCircle:
    def __init__(self, time, x, y):
        self.time = time
        self.x = x
        self.y = y

    def __str__(self):
        return "Circle: (%s,%s) at %s" % (self.x, self.y, self.time)

class Slider:
    def __init__(self, time, x, y, nodes, repeat, length, sv):
        self.time = time
        self.x = x
        self.y = y
        self.nodes = nodes
        self.repeat = repeat
        self.length = length * repeat
        self.sv = sv

    def __str__(self):
        return "Slider: \n\t(x,y): (%s,%s)\n\ttime: %s\n\tnodes: %s\n\trepeat: %s\n\tlength: %s\n\tslider velocity: %s" % (self.x, self.y, self.time, self.nodes, self.repeat, self.length, self.sv)

class Timing_Point:
    def __init__(self, offset, mpb, end=0):
        self.start_time = offset
        self.end_time = 7200000
        self.mpb = mpb
        self.bpm = 1 / mpb * 60000

    def __str__(self):
        return "time: %s\tBPM: %s" % (self.start_time, self.bpm)

class Beatmap:

    def __init__(self, loc):
        self.timing_points = list()
        self.objects = list()
        self.circles = list()
        self.sliders = list()
        def parse_beatmap(loc):
            sv = list()
            base_sv = 1
            with open(loc, "r", encoding='cp65001') as osu:
                class Section(Enum):
                    General = 0
                    Editor = 1
                    Metadata = 2
                    Difficulty = 3
                    Events = 4
                    TimingPoints = 5
                    Colours = 6
                    HitObjects = 7

                sec = ""

                i = osu.readlines()
                while len(i) > 0:
                    if i[0].startswith('[') and i[0].endswith(']\n'):
                        sec = i[0][1:-2]
                        i.pop(0)

                    if sec == "":
                        i.pop(0)
                        continue
                    
                    if Section[sec] == Section.General:
                        if i[0].startswith("StackLeniency: "):
                            self.stack_leniency = float(i[0][len("StackLeniency: "):])
                            i.pop(0)
                    
                    if Section[sec] == Section.Difficulty:
                        if i[0].startswith("HPDrainRate:"):
                            self.hp = float(i[0][len("HPDrainRate:"):])
                            i.pop(0)
                        if i[0].startswith("CircleSize:"):
                            self.cs = float(i[0][len("CircleSize:"):])
                            i.pop(0)
                        if i[0].startswith("OverallDifficulty:"):
                            self.od = float(i[0][len("OverallDifficulty:"):])
                            i.pop(0)
                        if i[0].startswith("ApproachRate:"):
                            self.ar = float(i[0][len("ApproachRate:"):])
                            i.pop(0)
                        if i[0].startswith("SliderMultiplier:"):
                            base_sv = float(i[0][len("SliderMultiplier:"):])
                            i.pop(0)
                        if i[0].startswith("SliderTickRate"):
                            self.tr = float(i[0][len("SliderTickRate:"):])
                            i.pop(0)
                    
                    if Section[sec] == Section.TimingPoints:
                        while Section[sec] == Section.TimingPoints:
                            if i[0] == "\n":
                                break
                            
                            t = [float(x) for x in i[0].split(",")]
                            if t[6] == 1.0:
                                self.timing_points.append(Timing_Point(t[0], t[1]))
                                if len(self.timing_points) > 1:
                                    self.timing_points[-2].end_time = self.timing_points[-1].start_time
                                
                            else:
                                
                                sv.append(((t[0], self.timing_points[-1].bpm * base_sv * 1 / (t[1] * (-1/100)))))

                            i.pop(0)

                    if Section[sec] == Section.HitObjects:
                        while Section[sec] == Section.HitObjects:
                            if len(i) == 0 or i[0] == "":
                                break
                            
                            h = i[0].split(",")
                            if int(h[3]) % 4 == 1:
                                hcirc = HitCircle(int(h[2]), int(h[0]), int(h[1]))
                                self.objects.append(hcirc)
                                self.circles.append(hcirc)

                            elif int(h[3]) % 4 == 2:
                                v = self.timing_points[0].bpm * base_sv
                                for u in sv:
                                    if int(u[0]) > int(h[2]):
                                          break
                                    v = u[1]
                                nodes = [(x.split(":")[0], x.split(":")[1]) for x in h[5][2:].split("|")]
                                length = float(h[7])
                                repeat = int(h[6])

                                slid = Slider(int(h[2]), int(h[0]), int(h[1]), nodes, repeat, length, v)
                                self.objects.append(slid)
                                self.sliders.append(slid)

                            i.pop(0)
                    if len(i) > 0:
                        i.pop(0)
                    
        parse_beatmap(loc)

        jump_patterns = list()
        pattern = list()
        beat_snap = -1
        prev = HitCircle(-100000, 0, 0)
        for i in self.objects:
            if not isinstance(i, Slider):
                bs = self.CalculateBeatSnap(prev, i)
            if isinstance(i, Slider):
                if len(pattern) > 1:
                    jump_patterns.append(pattern)
                pattern = list()
                continue
            if beat_snap != bs and beat_snap != 0:
                if len(pattern) > 1:
                    jump_patterns.append(pattern)
                pattern = list()
                pattern.append(i)
                beat_snap = 0
                prev = i
                continue
            prev = i
            pattern.append(i)
            beat_snap = bs
        if len(pattern) > 1:
            jump_patterns.append(pattern)
        self.jump_patterns = jump_patterns
            

    def __str__(self):
        s = "---Beatmap Stats---\nStack: %s\nHP: %s\nCS: %s\nOD: %s\nAR: %s\n\n---Timing Point---\n" % (self.stack_leniency, self.hp, self.cs, self.od, self.ar)
        for i in self.timing_points:
            s += "%s\n" % (i)

        s += "\n---Hit Objects---\n"
        for i in self.objects:
            s += "%s\n" % (i)

        return s
    
    @staticmethod
    def CalculateApproachWindow(ar):
        if ar <= 5:
            return 1800 - 120 * ar
        else:
            return 1200 - 150 * (ar - 5)

    def CalculateBeatSnap(self, obj1, obj2):
        'Only works if two objects are same bpm'
        if isinstance(obj1, Slider):
            pass
        else:
            bpm1 = self.get_timing_point(obj1)
            bpm2 = self.get_timing_point(obj2)
            beat = bpm1.mpb
            diff = (obj2.time - obj1.time)
            if bpm1 != bpm2:
                return -1
            else:
                if diff > beat:
                    return round(beat / (obj2.time - obj1.time), 2)
                else:
                    return round(beat / (obj2.time - obj1.time), 1)
    def get_timing_point(self, obj):
        time = obj.time
        t = self.timing_points[0]
        if len(self.timing_points) > 1:
            for i in self.timing_points:
                if i.start_time < time and i.end_time < time:
                    return i
        return t

def debug():
    b = Beatmap(r"D:\Game\osu!\Songs\332532 Panda Eyes & Teminite - Highscore\Panda Eyes & Teminite - Highscore (Fort) [Game Over].osu")
    print("end")
    for i in b.jump_patterns:
        print("-----")
        for j in i:
            print("%s" % (j))
        print("-----")
    pass

if __name__ == "__main__":
    debug()
