import tiledb
import numpy as np
from typing import Dict, Optional

class MedicalNarrativeDB:
    def __init__(self, db_uri="medical_narrative", tiles=None):
        self.db_uri = db_uri
        self.tiles = tiles

    def create_DBSchema(self):
        """
        Crea lo schema del database con una dimensione (patient_id) 
        e un attributo (clinical_notes)
        """
        try:
            # Crea la dimensione patient_id
            patient_id_dim = tiledb.Dim(name="patient_id", tile=self.tiles, dtype="ascii")
            
            # Crea il dominio con la dimensione
            domain = tiledb.Domain(patient_id_dim)

            # Crea l'attributo clinical_notes con compressione
            attrs = [
                tiledb.Attr(name="clinical_notes", 
                           dtype=str,
                           filters=tiledb.FilterList([tiledb.ZstdFilter(level=3)]))
            ]

            # Crea lo schema dell'array
            schema = tiledb.ArraySchema(
                domain=domain,
                attrs=attrs,
                sparse=True  # Usiamo sparse perché abbiamo stringhe come dimensioni
            )

            # Crea l'array TileDB
            tiledb.Array.create(self.db_uri, schema)
            print(f"Database {self.db_uri} creato con successo")
            
        except Exception as e:
            print(f"Errore durante la creazione del database: {e}")
            raise

    def search_patient(self, patient_id: str) -> Optional[Dict]:
        """
        Cerca i dati clinici di uno specifico paziente
        
        Args:
            patient_id: ID del paziente da cercare
            
        Returns:
            Dict con i dati del paziente o None se non trovato
        """
        try:
            with tiledb.open(self.db_uri, mode="r") as array:
                # Query per il paziente specifico
                #data = array.query(coords=True).df[patient_id]
                
                data = array.query(attrs=['clinical_notes']).df[patient_id]

                if data.empty:
                    return None
                
                # Converti il risultato in dizionario
                #patient_data = {
                #    'patient_id': patient_id,
                #    'clinical_notes': data['clinical_notes'].iloc[0]
                #}
                
                patient_data = data.iloc[0].to_dict()
                # Converti da bytes a string se necessario
                #if isinstance(patient_data['clinical_notes'], bytes):
                #patient_data['clinical_notes'] = patient_data['clinical_notes'].decode('utf-8')
                
                return patient_data
                
        except Exception as e:
            print(f"Errore durante la ricerca del paziente {patient_id}: {e}")
            return None

    def update_patient(self, patient_id: str, clinical_notes: str) -> bool:
        """
        Inserisce o aggiorna i dati clinici di uno specifico paziente
        
        Args:
            patient_id: ID del paziente
            clinical_notes: Note cliniche del paziente
            
        Returns:
            bool: True se l'operazione è riuscita, False altrimenti
        """
        try:
            with tiledb.open(self.db_uri, mode="w") as array:
                # Prepara i dati per l'inserimento
                data = {
                    'clinical_notes': np.array([clinical_notes])
                }
                
                # Esegui l'inserimento/aggiornamento
                array[patient_id] = data
                
                print(f"Dati del paziente {patient_id} inseriti/aggiornati con successo")
                return True
                
        except Exception as e:
            print(f"Errore durante l'inserimento/aggiornamento del paziente {patient_id}: {e}")
            return False

if __name__ == "__main__":

    # Crea un'istanza della classe
    db = MedicalNarrativeDB()

    # Crea il database
    db.create_DBSchema()

    # Inserisci dati per un paziente
    db.update_patient(
        "PAT001", 
        "Il paziente presenta febbre e mal di gola. Prescritta terapia antibiotica."
    )

    # Aggiorna i dati del paziente
    db.update_patient(
        "PAT001", 
        "Il paziente presenta febbre e mal di gola. Prescritta terapia antibiotica. \n" +
        "Follow-up: Sintomi in miglioramento dopo 3 giorni di terapia."
    )

    # Cerca i dati di un paziente
    patient_data = db.search_patient("PAT001")
    if patient_data:
        print(f"ID Paziente: {patient_data['patient_id']}")
        print(f"Note Cliniche: {patient_data['clinical_notes']}")
    else:
        print("Paziente non trovato")
