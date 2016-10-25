
from beatmap import Beatmap, HitCircle, Slider
import math

def Calculate_Momentum(beatmap):

    sum_constant = 1
    tendency_constant = 1/10
    consecutive_constant = .1
    distance_exponent = 1

    loaded = False
    x = 0
    y = 0
    t = 0
    m = (0, 0)
    sum = (0,0)
    q = 0

    for j in beatmap.jump_patterns:
        s = (0,0)
        for i in j:            
            
            if not loaded:
                x = i.x
                y = i.y
                t = i.time
                m = (0, 0)
                loaded = True

            else:
                xt = i.x ** distance_exponent
                yt = i.y ** distance_exponent
                tt = i.time
                #The "tendency"
                mp = (m[0] * -1 * tendency_constant, m[1] * -1 * tendency_constant)

                #momentum required = distance / time
                mt= ((xt - x) / (tt - t), (yt - y) / (tt - t))

                #total momentum
                tm = (mt[0] - mp[0], mt[1] - mp[1])
                xz = tm[0]
                yz = tm[1]

                tm = (xz, yz)

                s = (s[0] + tm[0] * (q * consecutive_constant), s[1] + tm[1] * (q * consecutive_constant))
                #print("%s ~ %s | (%s,%s) -> (%s,%s): %s" % (t, tt, x, y, xt, yt, tm))
                x = xt
                y = yt
                t = tt
                m = mt
                q += 1
        sum = (sum[0] + s[0], sum[1] + s[1])
        s = (0,0)
        q = 0
        loaded = False

    
    return math.sqrt(sum[0] ** 2 + sum[1] ** 2) * sum_constant

def debug():
    game_over = Beatmap(r"D:\Game\osu!\Songs\332532 Panda Eyes & Teminite - Highscore\Panda Eyes & Teminite - Highscore (Fort) [Game Over].osu")
    stella = Beatmap(r"D:\Game\osu!\Songs\stell ed\Tamaki to Yumine (CV Naganawa Maria Maekawa Ryouko) - Yonaka Jikaru (-[Koinuri]) [Stella].osu")
    dark_dreamer = Beatmap(r"D:\Game\osu!\Songs\\185250 ALiCE'S EMOTiON - Dark Flight Dreamer\ALiCE'S EMOTiON - Dark Flight Dreamer (Sakaue Nachi) [Dreamer].osu")
    maze = Beatmap(r"D:\Game\osu!\Songs\10031 Savage Genius feat Oomi Tomoe - Maze (TV-Size)\Savage Genius feat. Oomi Tomoe - Maze (TV-Size) (alvisto) [Maze].osu")
    airman = Beatmap(r"D:\Game\osu!\Songs\24313 Team Nekokan - Can't Defeat Airman\Team Nekokan - Can't Defeat Airman (Blue Dragon) [Holy Shit! It's Airman!!].osu")
    no_title = Beatmap(r"D:\Game\osu!\Songs\320118 Reol - No title\Reol - No title (VINXIS) [jieusieu's Lemur].osu")
    blue_zenith = Beatmap(r"D:\Game\osu!\Songs\\292301 xi - Blue Zenith\xi - Blue Zenith (Asphyxia) [FOUR DIMENSIONS].osu")

    print("Random 3.33 star TV Size: %s" % Calculate_Momentum(maze))
    print("My Stella map with lots of flowy jump: %s" % Calculate_Momentum(stella))
    print("Dark Flight Dreamer (pp farm with several stream): %s" % Calculate_Momentum(dark_dreamer))
    print("No Title (Lemur diff): %s" % Calculate_Momentum(no_title))
    print("Airman: %s" % Calculate_Momentum(airman))
    print("Highscore (Game Over): %s" % Calculate_Momentum(game_over))
    print("Blue Zenith: %s" % Calculate_Momentum(blue_zenith))
    

if __name__ == "__main__":
    debug()