from abc import ABC, abstractmethod

class Observador(ABC):
    @abstractmethod
    def atualizar(self, evento: dict) -> None:
        pass

class Observavel():
    def __init__(self):
        self._observadores = []

    def anexar(self, observador: Observador) -> None:
        if observador not in self._observadores:
            self._observadores.append(observador)

    def desanexar(self, observador: Observador) -> None:
        if observador in self._observadores:
            self._observadores.remove(observador)

    def notificar(self, evento: dict) -> None:
        for obs in self._observadores:
            try:
                obs.atualizar(evento)
            except Exception as erro:
                print(f"[Observavel] falha notificando {obs}: {erro}")

