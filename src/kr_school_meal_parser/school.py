class School:
    class Region:
        BUSAN = "stu.pen.go.kr"
        CHUNGBUK = "stu.cbe.go.kr"
        CHUNGNAM = "stu.cne.go.kr"
        DAEJEON = "stu.dge.go.kr"
        DEAGU = "stu.dge.go.kr"
        GWANGJU = "stu.gen.go.kr"
        GYEONGBUK = "stu.gbe.go.kr"
        GYEONGGI = "stu.goe.go.kr"
        GYEONGNAM = "stu.gne.go.kr"
        INCHEON = "stu.ice.go.kr"
        JEJU = "stu.jje.go.kr"
        JEONBUK = "stu.jbe.go.kr"
        JEONNAM = "stu.jne.go.kr"
        KANGWON = "stu.kwe.go.kr"
        SEJONG = "stu.sje.go.kr"
        SEOUL = "stu.sen.go.kr"
        ULSAN = "stu.use.go.kr"

    class Type:
        KINDERGARTEN = 1
        ELEMENTARY = 2
        MIDDLE = 3
        HIGH = 4

    def __init__(self, school_region, school_type, school_code):
        self.region = school_region
        self.type = school_type
        self.code = school_code
