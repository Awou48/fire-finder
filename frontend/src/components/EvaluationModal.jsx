import { X, Activity } from 'lucide-react'
import { API_URL } from '../config'

const EvaluationModal = ({ onClose }) => {
  return (
    <div className="fixed inset-0 z-[1000] bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-slate-800 p-6 rounded-2xl border border-slate-700 shadow-2xl flex flex-col items-center w-full max-w-lg animate-in fade-in zoom-in duration-300">
        <div className="flex justify-between w-full mb-4 border-b border-slate-700 pb-2">
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <Activity className="text-purple-500" /> PERFORMA MODEL AI
          </h2>
          <button onClick={onClose} className="text-slate-400 hover:text-red-500 transition-colors bg-slate-700/50 p-1 rounded-full"><X size={20} /></button>
        </div>
        <div className="bg-white p-2 rounded-xl shadow-inner w-full flex justify-center min-h-[300px] items-center">
            <img src={`${API_URL}/performance/matrix`} alt="Loading Matrix..." className="rounded max-h-[400px] object-contain"
                onError={(e) => { e.target.style.display = 'none'; e.target.parentNode.innerHTML = '<span class="text-red-500 text-sm font-bold">Gagal memuat grafik. Cek Backend.</span>'; }} />
        </div>
        <div className="mt-4 bg-slate-900/50 p-3 rounded-lg border border-slate-700 w-full">
            <h4 className="text-xs font-bold text-slate-300 mb-1">CARA BACA MATRIKS:</h4>
            <ul className="text-[10px] text-slate-400 space-y-1 list-disc list-inside">
                <li><strong className="text-red-400">Kanan Bawah:</strong> Deteksi Api Sukses.</li>
                <li><strong className="text-slate-400">Kiri Atas:</strong> Deteksi Aman Sukses.</li>
            </ul>
        </div>
      </div>
    </div>
  )
}
export default EvaluationModal