from abc import ABC, abstractmethod


class qddcf_0(ABC):
    @abstractmethod
    def qddcf_2(self):
        raise NotImplementedError

    def qddcf_3(self):
        return self.qddcf_2()


class qddcf_1(qddcf_0):
    def qddcf_2(self):
        return 4


qddcf_1().qddcf_3()
