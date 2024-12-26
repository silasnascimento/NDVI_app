from flask import Flask, request, jsonify
from flask_cors import CORS
import ee

# Inicializa o GEE
try:
    ee.Initialize()
except Exception as e:
    print("Erro ao inicializar o Google Earth Engine:", e)

app = Flask(__name__)
CORS(app)  # Habilita CORS

@app.route('/calculate_ndvi', methods=['POST'])
def calculate_ndvi():
    try:
        data = request.json
        roi = ee.Geometry.Polygon(data['roi']['coordinates'])  # Converte GeoJSON em geometria GEE

        # Calcula NDVI
        image = (ee.ImageCollection("COPERNICUS/S2")
                 .filterDate('2024-01-01', '2024-01-31')
                 .filterBounds(roi)
                 .median()
                 .normalizedDifference(['B8', 'B4'])
                 .rename('NDVI')
                .clip(roi))

        # Calcula NDVI médio
        stats = image.reduceRegion(reducer=ee.Reducer.mean(), geometry=roi, scale=10)
        ndvi_mean = stats.get('NDVI').getInfo()

        return jsonify({'ndvi_mean': ndvi_mean})
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/get_ndvi_tiles', methods=['POST'])
def get_ndvi_tiles():
    try:
        data = request.json
        roi = ee.Geometry.Polygon(data['roi']['coordinates'])  # Converte GeoJSON em geometria GEE

        # Calcula NDVI
        ndvi = (ee.ImageCollection("COPERNICUS/S2")
                .filterBounds(roi)
                .filterDate('2024-01-01', '2024-01-31')
                .median()
                .normalizedDifference(['B8', 'B4'])
                .rename('NDVI')
                .clip(roi))

        # Gera o mapa NDVI como tiles
        ndvi_vis_params = {'min': 0, 'max': 0.8, 'palette': ['red', 'yellow', 'green']}
        map_id_dict = ndvi.getMapId(ndvi_vis_params)

        # Retorna o URL dos tiles
        return jsonify({
            'tile_url': map_id_dict['tile_fetcher'].url_format
        })

    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
