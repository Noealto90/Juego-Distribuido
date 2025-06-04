from firebase_admin import firestore
from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from controlador.central_reutilizable import monitorear_carga

class ScoreManager:
    def __init__(self):
        self.db = firestore.client()
    
    def update_score(self, player_id, game_id, score):
        """
        Actualiza la puntuación de un jugador
        """
        # Actualizar puntuación del juego
        game_ref = self.db.collection('juegos').document(game_id)
        game_ref.update({
            'puntuacion': score,
            'fecha_actualizacion': datetime.now().isoformat()
        })
        
        # Actualizar puntuación del jugador
        player_ref = self.db.collection('jugadores').document(player_id)
        player_data = player_ref.get()
        
        if player_data.exists:
            current_data = player_data.to_dict()
            high_score = current_data.get('puntuacion_maxima', 0)
            games_played = current_data.get('partidas_jugadas', 0)
            
            player_ref.update({
                'puntuacion_maxima': max(high_score, score),
                'partidas_jugadas': games_played + 1,
                'ultima_partida': game_id,
                'fecha_actualizacion': datetime.now().isoformat()
            })
        else:
            player_ref.set({
                'puntuacion_maxima': score,
                'partidas_jugadas': 1,
                'ultima_partida': game_id,
                'fecha_creacion': datetime.now().isoformat(),
                'fecha_actualizacion': datetime.now().isoformat()
            })
        
        # Monitorear actualización
        monitorear_carga(
            f"score_{game_id}",
            "puntuacion",
            "actualizada",
            {"player_id": player_id, "score": score}
        )
        
        return True
    
    def get_leaderboard(self, limit=10):
        """
        Obtiene la tabla de clasificación
        """
        players = self.db.collection('jugadores')\
            .order_by('puntuacion_maxima', direction=firestore.Query.DESCENDING)\
            .limit(limit)\
            .get()
        
        return [player.to_dict() for player in players]
    
    def get_player_stats(self, player_id):
        """
        Obtiene estadísticas de un jugador
        """
        player_ref = self.db.collection('jugadores').document(player_id)
        player_data = player_ref.get()
        
        if player_data.exists:
            return player_data.to_dict()
        return None 