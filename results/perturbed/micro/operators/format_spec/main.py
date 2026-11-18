class q0aa5_0:
    def __format__(self, spec):
        return "1.00"

    def __str__(self):
        return "1"


money = q0aa5_0()
text = f"{money:.2f}"
format(money, "x")
