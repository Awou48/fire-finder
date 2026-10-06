import { useState, useEffect } from 'react'
import axios from 'axios'
import { MapContainer, TileLayer, Marker, Popup, Circle, Polyline } from 'react-leaflet'
import 'leaflet/dist/leaflet.css'
import { AlertTriangle, Activity, Calendar, Flame, Thermometer, Wind, Radio, CloudRain, Plane, History, X, FileText } from 'lucide-react'
import L from 'leaflet';
import EvaluationModal from './components/EvaluationModal'
import { API_URL } from './config'

const getCustomIcon = (color) => {
  let iconUrl = 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-red.png';
  if(color === 'orange') iconUrl = 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-orange.png';
  if(color === 'yellow') iconUrl = 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-gold.png';
  if(color === 'blue') iconUrl = 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-blue.png';
  return new L.Icon({ iconUrl, shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png', iconSize: [25, 41], iconAnchor: [12, 41], popupAnchor: [1, -34], shadowSize: [41, 41] });
};

function App() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [forecastDay, setForecastDay] = useState(1)
  const [advisorLoading, setAdvisorLoading] = useState(false)
  const [advisorReply, setAdvisorReply] = useState(null)
  const [missionPath, setMissionPath] = useState(null)
  const [historyLogs, setHistoryLogs] = useState([])
  const [showHistoryModal, setShowHistoryModal] = useState(false)
  const [showMatrixModal, setShowMatrixModal] = useState(false)

  const fetchData = async (day) => {
    setLoading(true); setMissionPath(null);
    try {
      const response = await axios.get(`${API_URL}/predict/future?days=${day}`)
      setData(response.data); setLoading(false)
    } catch (error) { console.error(error); setLoading(false) }
  }

  const fetchHistory = async () => {
    try { const res = await axios.get(`${API_URL}/history?limit=15`); setHistoryLogs(res.data); setShowHistoryModal(true) } catch { alert("Gagal DB") }
  }

  const calculateMission = async (lat, lon) => {
    setMissionPath(null);
    try {
      const res = await axios.post(`${API_URL}/calculate-mission`, { target_lat: lat, target_lon: lon })
      if (res.data && res.data.source && res.data.target) setMissionPath(res.data)
    } catch { alert("Gagal Rute") }
  }

  const askAIAdvisor = async () => {
    if (!data) return; setAdvisorLoading(true);
    const summary = `Status ${data.status_summary}, Total ${data.hotspots?.length ?? 0} Hotspot.`;
    try { const res = await axios.post(`${API_URL}/ask-advisor`, { summary_text: summary }); setAdvisorReply(res.data.reply); } 
    catch { setAdvisorReply("Gagal AI."); } finally { setAdvisorLoading(false); }
  };

  useEffect(() => { fetchData(forecastDay) }, [forecastDay])

  return (
    <div className="min-h-screen bg-slate-900 text-white font-sans selection:bg-orange-500 selection:text-white relative">
      <header className="bg-slate-800/90 backdrop-blur p-4 border-b border-slate-700 sticky top-0 z-40 flex justify-between items-center px-6 shadow-lg">
        <div className="flex items-center gap-3">
          <div className="bg-gradient-to-tr from-red-600 to-orange-500 p-2 rounded-lg shadow-lg"><Flame size={24} className="text-white fill-white" /></div>
          <div><h1 className="text-xl font-bold tracking-wider">FIREFINDER <span className="text-orange-400">ULTIMATE</span></h1><p className="text-[10px] text-slate-400 uppercase tracking-widest">Autonomous Response System</p></div>
        </div>
        <div className="flex items-center gap-2">
            <button onClick={() => setShowMatrixModal(true)} className="flex items-center gap-2 px-4 py-2 bg-slate-700 hover:bg-slate-600 rounded-lg text-xs font-bold border border-slate-600 transition-all"><Activity size={16} className="text-purple-400"/> EVALUASI AI</button>
            <button onClick={fetchHistory} className="flex items-center gap-2 px-4 py-2 bg-slate-700 hover:bg-slate-600 rounded-lg text-xs font-bold border border-slate-600 transition-all"><History size={16} className="text-blue-400"/> DATA LOGS</button>
        </div>
      </header>

      <main className="p-4 grid grid-cols-1 lg:grid-cols-12 gap-4 h-[calc(100vh-80px)]">
        <div className="lg:col-span-4 flex flex-col gap-4 h-full overflow-hidden">
          <div className="bg-slate-800 p-4 rounded-xl border border-slate-700 shadow-lg">
            <div className="flex justify-between items-center mb-3"><h2 className="flex items-center gap-2 text-sm font-bold text-slate-200"><Calendar size={16} className="text-blue-400" /> TIMELINE</h2><span className="bg-blue-600 text-white px-2 py-0.5 rounded text-xs font-bold">H+{forecastDay}</span></div>
            <input type="range" min="1" max="7" value={forecastDay} onChange={(e) => setForecastDay(parseInt(e.target.value))} className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-blue-500"/>
          </div>
          <div className="bg-slate-800 p-4 rounded-xl border border-slate-700 grid grid-cols-2 gap-2">
              <div className="col-span-2 flex items-center gap-2 text-xs font-bold text-slate-400 mb-1"><CloudRain size={14} className="text-cyan-400" /> CUACA REAL-TIME</div>
              <div className="bg-slate-900/50 p-2 rounded-lg border border-slate-700/50 flex items-center gap-2"><Thermometer size={18} className="text-yellow-500" /><div><span className="text-[10px] text-slate-500 block">SUHU</span><span className="font-mono text-sm font-bold">{data?.main_weather?.temp || '-'}</span></div></div>
              <div className="bg-slate-900/50 p-2 rounded-lg border border-slate-700/50 flex items-center gap-2"><Wind size={18} className="text-cyan-500" /><div><span className="text-[10px] text-slate-500 block">ANGIN</span><span className="font-mono text-sm font-bold">{data?.main_weather?.wind || '-'}</span></div></div>
          </div>
          <div className="bg-gradient-to-br from-slate-800 to-slate-900 p-4 rounded-xl border border-blue-500/30 flex flex-col flex-grow relative overflow-hidden">
             <div className="flex items-center justify-between mb-2 relative z-10"><h3 className="flex items-center gap-2 text-sm font-bold text-blue-300"><Radio size={16} className={advisorLoading ? "animate-ping" : ""} /> AI COMMAND CENTER</h3></div>
             <div className="flex-grow bg-slate-950/50 rounded-lg p-3 text-xs text-slate-300 font-mono mb-3 border border-slate-700/50 overflow-y-auto max-h-[200px] custom-scrollbar">
                {advisorLoading ? <span className="animate-pulse">Menghubungi Markas Pusat...</span> : advisorReply ? <div className="whitespace-pre-line text-emerald-400">{">"} {advisorReply}</div> : <span className="text-slate-600 opacity-50">Menunggu instruksi...</span>}
             </div>
             <button onClick={askAIAdvisor} disabled={loading || advisorLoading} className="w-full bg-blue-600 hover:bg-blue-500 disabled:bg-slate-700 text-white text-xs font-bold py-3 rounded-lg transition-all shadow-lg relative z-10">{advisorLoading ? 'MENERIMA TRANSMISI...' : 'MINTA INSTRUKSI TAKTIS'}</button>
          </div>
        </div>

        <div className="lg:col-span-8 bg-slate-800 rounded-xl overflow-hidden border border-slate-700 relative shadow-2xl z-0">
          <MapContainer center={[-1.5, 113.5]} zoom={6} style={{ height: '100%', width: '100%' }}>
            <TileLayer url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}" attribution='Tiles &copy; Esri' />
            {!loading && data?.hotspots?.map((spot, idx) => (
              <div key={idx}>
                <Marker position={[spot.lat, spot.lon]} icon={getCustomIcon(spot.color)}>
                  <Popup><div className="text-center"><b className="uppercase text-slate-800">{spot.region}</b><br/><span className={`font-bold ${spot.color === 'red' ? 'text-red-600' : 'text-orange-500'}`}>{spot.level} ({spot.prob}%)</span><button onClick={() => calculateMission(spot.lat, spot.lon)} className="mt-2 w-full bg-slate-800 text-white text-xs py-1.5 rounded hover:bg-slate-700 transition-colors flex items-center justify-center gap-1 border border-slate-600"><Plane size={12}/> DEPLOY DRONE</button></div></Popup>
                </Marker>
                {spot.color === 'red' && <Circle center={[spot.lat, spot.lon]} pathOptions={{ color: 'red', fillColor: 'red', fillOpacity: 0.15 }} radius={15000} />}
              </div>
            ))}
            {missionPath && missionPath.source && missionPath.target && (
              <>
                <Polyline positions={[[missionPath.source.lat, missionPath.source.lon], [missionPath.target.lat, missionPath.target.lon]]} pathOptions={{ color: 'cyan', weight: 4, dashArray: '10, 15', opacity: 0.9 }} />
                <Marker position={[missionPath.source.lat, missionPath.source.lon]} icon={getCustomIcon('blue')}><Popup><b className="text-blue-600">🚀 DRONE DILUNCURKAN</b><br/>ETA: {missionPath.eta_minutes} menit</Popup></Marker>
              </>
            )}
          </MapContainer>
        </div>
      </main>

      {showHistoryModal && (
        <div className="fixed inset-0 z-[1000] bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
            <div className="bg-slate-800 w-full max-w-4xl rounded-2xl border border-slate-700 shadow-2xl overflow-hidden flex flex-col max-h-[80vh]">
                <div className="p-4 border-b border-slate-700 flex justify-between items-center bg-slate-900/50"><h2 className="flex items-center gap-2 text-lg font-bold text-white"><FileText className="text-blue-500"/> DATA LOGS</h2><button onClick={() => setShowHistoryModal(false)} className="p-2 hover:bg-red-500/20 rounded-full hover:text-red-500 transition-colors"><X size={20}/></button></div>
                <div className="overflow-y-auto p-4 custom-scrollbar">
                    <table className="w-full text-left border-collapse">
                        <thead><tr className="text-slate-400 text-xs uppercase border-b border-slate-700"><th className="p-3">Waktu</th><th className="p-3">Wilayah</th><th className="p-3">Level</th><th className="p-3">Cuaca</th></tr></thead>
                        <tbody className="text-sm">{historyLogs.map((log) => (<tr key={log.id} className="border-b border-slate-700/50 hover:bg-slate-700/30"><td className="p-3 font-mono text-slate-300">{new Date(log.timestamp).toLocaleString()}</td><td className="p-3 font-bold text-white">{log.region}</td><td className="p-3"><span className="bg-red-500/20 text-red-400 px-2 py-1 rounded text-xs font-bold">{log.level} ({log.confidence}%)</span></td><td className="p-3 text-slate-300 text-xs">{log.temp} | {log.wind}</td></tr>))}</tbody>
                    </table>
                </div>
            </div>
        </div>
      )}

      {showMatrixModal && <EvaluationModal onClose={() => setShowMatrixModal(false)} />}
    </div>
  )
}
export default App