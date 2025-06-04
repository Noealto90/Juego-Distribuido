from firebase_admin import firestore
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from controlador.central_reutilizable import obtener_datos, monitorear_carga

class LoadBalancer:
    def __init__(self):
        self.db = firestore.client()
        
    def get_node_load(self, node_id):
        """
        Obtiene la carga actual de un nodo
        """
        node_ref = self.db.collection('nodos').document(node_id)
        node_data = node_ref.get()
        
        if node_data.exists:
            return node_data.to_dict().get('cpu', 100)
        return 100
    
    def find_best_node(self):
        """
        Encuentra el nodo con menor carga
        """
        nodes = self.db.collection('nodos').get()
        if not nodes:
            return None
            
        return min(nodes, key=lambda x: self.get_node_load(x.id))
    
    def redistribute_games(self):
        """
        Redistribuye los juegos entre nodos según la carga
        """
        nodes = self.db.collection('nodos').get()
        active_games = self.db.collection('juegos').where('estado', '==', 'activo').get()
        
        # Ordenar nodos por carga
        sorted_nodes = sorted(nodes, key=lambda x: self.get_node_load(x.id))
        
        # Redistribuir juegos
        for i, game in enumerate(active_games):
            target_node = sorted_nodes[i % len(sorted_nodes)]
            game.reference.update({
                'nodo_asignado': target_node.id
            })
            
            # Monitorear la redistribución
            monitorear_carga(
                game.id,
                "juego",
                "redistribuido",
                {"nodo_asignado": target_node.id}
            )
        
        return True 