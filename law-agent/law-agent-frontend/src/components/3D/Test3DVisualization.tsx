import React from 'react';
import { Canvas } from '@react-three/fiber';
import CourtProcessFlow3D from './CourtProcessFlow3D';
import JurisdictionalMap3D from './JurisdictionalMap3D';

const Test3DVisualization: React.FC = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-black p-8">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-4xl font-bold text-white text-center mb-12">
          3D Legal Visualization Test
        </h1>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Court Process Flow Visualization */}
          <div className="bg-black/50 rounded-2xl p-6 border border-blue-500/30">
            <h2 className="text-2xl font-bold text-white mb-4">Court Process Flow</h2>
            <div className="h-96 rounded-xl overflow-hidden bg-gradient-to-br from-gray-900 to-blue-900">
              <Canvas
                camera={{ position: [0, 5, 15], fov: 60 }}
                style={{ background: 'linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #334155 100%)' }}
              >
                <CourtProcessFlow3D
                  processType="criminal"
                  showTimeline={true}
                  animationSpeed={1}
                />
              </Canvas>
            </div>
            <p className="text-gray-300 mt-4 text-center">
              Interactive 3D visualization of criminal court process flow
            </p>
          </div>
          
          {/* Jurisdictional Map Visualization */}
          <div className="bg-black/50 rounded-2xl p-6 border border-purple-500/30">
            <h2 className="text-2xl font-bold text-white mb-4">Jurisdictional Map</h2>
            <div className="h-96 rounded-xl overflow-hidden bg-gradient-to-br from-gray-900 to-purple-900">
              <Canvas
                camera={{ position: [0, 5, 10], fov: 60 }}
                style={{ background: 'linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #334155 100%)' }}
              >
                <JurisdictionalMap3D
                  region="india"
                  showCourts={true}
                  showCaseLoad={true}
                />
              </Canvas>
            </div>
            <p className="text-gray-300 mt-4 text-center">
              Interactive 3D visualization of legal jurisdictions
            </p>
          </div>
        </div>
        
        <div className="mt-12 text-center">
          <h2 className="text-3xl font-bold text-white mb-6">Features</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-blue-900/30 p-6 rounded-xl border border-blue-500/30">
              <div className="text-4xl mb-4">⚖️</div>
              <h3 className="text-xl font-bold text-white mb-2">Interactive 3D Models</h3>
              <p className="text-gray-300">
                Fully interactive 3D visualizations of court processes and legal jurisdictions
              </p>
            </div>
            
            <div className="bg-purple-900/30 p-6 rounded-xl border border-purple-500/30">
              <div className="text-4xl mb-4">🔄</div>
              <h3 className="text-xl font-bold text-white mb-2">Real-time Animation</h3>
              <p className="text-gray-300">
                Dynamic animations showing the flow of legal processes and jurisdictional relationships
              </p>
            </div>
            
            <div className="bg-green-900/30 p-6 rounded-xl border border-green-500/30">
              <div className="text-4xl mb-4">🎯</div>
              <h3 className="text-xl font-bold text-white mb-2">Detailed Information</h3>
              <p className="text-gray-300">
                Hover over elements to view detailed information about each step or jurisdiction
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Test3DVisualization;