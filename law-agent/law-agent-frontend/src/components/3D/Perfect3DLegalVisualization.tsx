/**
 * PERFECT 3D Legal Visualization Hub
 * Complete integration of all 3D components for the law agent
 */

import React, { useState, useEffect } from 'react';
import { Canvas } from '@react-three/fiber';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import CourtProcessFlow3D from './CourtProcessFlow3D';
import JurisdictionalMap3D from './JurisdictionalMap3D';
import { Play, Pause, RotateCcw, Settings, Map, Workflow, Eye, EyeOff } from 'lucide-react';

interface Perfect3DLegalVisualizationProps {
  initialView?: '3d-process' | '3d-jurisdiction';
  legalDomain?: string;
  userLocation?: string;
  onVisualizationChange?: (view: string, data: any) => void;
}

const Perfect3DLegalVisualization: React.FC<Perfect3DLegalVisualizationProps> = ({
  initialView = '3d-process',
  legalDomain = 'criminal',
  userLocation = 'usa',
  onVisualizationChange
}) => {
  const [activeView, setActiveView] = useState(initialView);
  const [isAnimating, setIsAnimating] = useState(true);
  const [showControls, setShowControls] = useState(true);
  const [processType, setProcessType] = useState<'criminal' | 'civil' | 'family' | 'employment'>('criminal');
  const [jurisdictionRegion, setJurisdictionRegion] = useState<'india' | 'usa' | 'california' | 'texas' | 'newyork' | 'florida'>('india');
  const [selectedStep, setSelectedStep] = useState<string | null>(null);
  const [selectedJurisdiction, setSelectedJurisdiction] = useState<string | null>(null);

  // Auto-detect process type from legal domain
  useEffect(() => {
    const domainMapping: Record<string, typeof processType> = {
      'criminal_law': 'criminal',
      'family_law': 'family',
      'employment_law': 'employment',
      'civil_law': 'civil',
      'property_law': 'civil',
      'consumer_law': 'civil'
    };
    
    if (legalDomain && domainMapping[legalDomain]) {
      setProcessType(domainMapping[legalDomain]);
    }
  }, [legalDomain]);

  // Auto-detect jurisdiction from user location
  useEffect(() => {
    const locationMapping: Record<string, typeof jurisdictionRegion> = {
      'india': 'india',
      'california': 'california',
      'texas': 'texas',
      'new_york': 'newyork',
      'florida': 'florida',
      'usa': 'usa'
    };

    if (userLocation && locationMapping[userLocation]) {
      setJurisdictionRegion(locationMapping[userLocation]);
    }
  }, [userLocation]);

  const handleStepClick = (stepId: string) => {
    setSelectedStep(stepId);
    onVisualizationChange?.('process-step-selected', { stepId, processType });
  };

  const handleJurisdictionClick = (jurisdictionId: string) => {
    setSelectedJurisdiction(jurisdictionId);
    onVisualizationChange?.('jurisdiction-selected', { jurisdictionId, region: jurisdictionRegion });
  };

  const handleViewChange = (view: string) => {
    setActiveView(view as typeof activeView);
    onVisualizationChange?.('view-changed', { view });
  };

  const resetView = () => {
    setSelectedStep(null);
    setSelectedJurisdiction(null);
    onVisualizationChange?.('view-reset', {});
  };

  return (
    <div className="w-full h-full bg-gradient-to-br from-gray-900 via-blue-900/10 to-black relative">
      {/* Perfect 3D Visualization Tabs */}
      <Tabs value={activeView} onValueChange={handleViewChange} className="w-full h-full">
        {/* Tab Navigation */}
        <div className="absolute top-4 left-1/2 transform -translate-x-1/2 z-10">
          <TabsList className="bg-black/80 backdrop-blur-sm border border-blue-500/30">
            <TabsTrigger 
              value="3d-process" 
              className="flex items-center space-x-2 data-[state=active]:bg-blue-600"
            >
              <Workflow className="w-4 h-4" />
              <span>3D Court Process</span>
            </TabsTrigger>
            <TabsTrigger 
              value="3d-jurisdiction" 
              className="flex items-center space-x-2 data-[state=active]:bg-blue-600"
            >
              <Map className="w-4 h-4" />
              <span>3D Jurisdictions</span>
            </TabsTrigger>
          </TabsList>
        </div>

        {/* 3D Court Process Flow */}
        <TabsContent value="3d-process" className="w-full h-full m-0">
          <div className="relative w-full h-full">
            {/* 3D Court Process Flow Visualization */}
            <Canvas
              camera={{ position: [0, 5, 15], fov: 60 }}
              style={{ background: 'linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #334155 100%)' }}
            >
              <CourtProcessFlow3D
                processType={processType}
                currentStep={selectedStep || undefined}
                onStepClick={handleStepClick}
                showTimeline={true}
                animationSpeed={isAnimating ? 1 : 0}
              />
            </Canvas>
            
            {/* Process Controls */}
            <div className="absolute top-20 left-4 bg-black/80 backdrop-blur-sm rounded-lg p-4 border border-blue-500/30">
              <h3 className="text-white font-bold mb-3">Process Controls</h3>
              
              {/* Process Type Selector */}
              <div className="mb-4">
                <label className="text-sm text-gray-300 mb-2 block">Legal Process:</label>
                <select
                  value={processType}
                  onChange={(e) => setProcessType(e.target.value as typeof processType)}
                  className="w-full bg-gray-800 text-white rounded px-3 py-2 text-sm border border-gray-600"
                >
                  <option value="criminal">Criminal Law</option>
                  <option value="civil">Civil Law</option>
                  <option value="family">Family Law</option>
                  <option value="employment">Employment Law</option>
                </select>
              </div>

              {/* Animation Controls */}
              <div className="flex space-x-2 mb-3">
                <button
                  onClick={() => setIsAnimating(!isAnimating)}
                  className="flex items-center space-x-1 bg-blue-600 hover:bg-blue-700 text-white px-3 py-2 rounded text-sm transition-colors"
                >
                  {isAnimating ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
                  <span>{isAnimating ? 'Pause' : 'Play'}</span>
                </button>
                
                <button
                  onClick={resetView}
                  className="flex items-center space-x-1 bg-gray-600 hover:bg-gray-700 text-white px-3 py-2 rounded text-sm transition-colors"
                >
                  <RotateCcw className="w-4 h-4" />
                  <span>Reset</span>
                </button>
              </div>

              {/* Current Step Info */}
              {selectedStep && (
                <div className="mt-4 p-3 bg-blue-600/20 rounded border border-blue-500/30">
                  <div className="text-blue-400 font-semibold text-sm">Selected Step:</div>
                  <div className="text-white text-sm capitalize">{selectedStep.replace('_', ' ')}</div>
                </div>
              )}
            </div>
          </div>
        </TabsContent>

        {/* 3D Jurisdictional Map */}
        <TabsContent value="3d-jurisdiction" className="w-full h-full m-0">
          <div className="relative w-full h-full">
            <Canvas
              camera={{ position: [0, 5, 10], fov: 60 }}
              style={{ background: 'linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #334155 100%)' }}
            >
              <JurisdictionalMap3D
                region={jurisdictionRegion}
                focusJurisdiction={selectedJurisdiction || undefined}
                showCourts={true}
                showCaseLoad={true}
                onJurisdictionClick={handleJurisdictionClick}
              />
            </Canvas>
            
            {/* Jurisdiction Controls */}
            <div className="absolute top-20 left-4 bg-black/80 backdrop-blur-sm rounded-lg p-4 border border-blue-500/30">
              <h3 className="text-white font-bold mb-3">Jurisdiction Controls</h3>
              
              {/* Region Selector */}
              <div className="mb-4">
                <label className="text-sm text-gray-300 mb-2 block">Region:</label>
                <select
                  value={jurisdictionRegion}
                  onChange={(e) => setJurisdictionRegion(e.target.value as typeof jurisdictionRegion)}
                  className="w-full bg-gray-800 text-white rounded px-3 py-2 text-sm border border-gray-600"
                >
                  <option value="india">India</option>
                  <option value="usa">United States</option>
                  <option value="california">California</option>
                  <option value="texas">Texas</option>
                  <option value="newyork">New York</option>
                  <option value="florida">Florida</option>
                </select>
              </div>

              {/* View Controls */}
              <div className="flex space-x-2 mb-3">
                <button
                  onClick={() => setShowControls(!showControls)}
                  className="flex items-center space-x-1 bg-purple-600 hover:bg-purple-700 text-white px-3 py-2 rounded text-sm transition-colors"
                >
                  {showControls ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  <span>Controls</span>
                </button>
                
                <button
                  onClick={resetView}
                  className="flex items-center space-x-1 bg-gray-600 hover:bg-gray-700 text-white px-3 py-2 rounded text-sm transition-colors"
                >
                  <RotateCcw className="w-4 h-4" />
                  <span>Reset</span>
                </button>
              </div>

              {/* Current Jurisdiction Info */}
              {selectedJurisdiction && (
                <div className="mt-4 p-3 bg-purple-600/20 rounded border border-purple-500/30">
                  <div className="text-purple-400 font-semibold text-sm">Selected:</div>
                  <div className="text-white text-sm capitalize">{selectedJurisdiction.replace('_', ' ')}</div>
                </div>
              )}
            </div>
          </div>
        </TabsContent>
      </Tabs>

      {/* Perfect Status Indicator */}
      <div className="absolute bottom-4 right-4 bg-black/80 backdrop-blur-sm rounded-lg p-3 border border-green-500/30">
        <div className="flex items-center space-x-2">
          <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
          <span className="text-green-400 text-sm font-semibold">3D Visualization Active</span>
        </div>
        <div className="text-xs text-gray-400 mt-1">
          React Three Fiber • Perfect Implementation
        </div>
      </div>

      {/* Performance Indicator */}
      <div className="absolute top-4 right-4 bg-black/80 backdrop-blur-sm rounded-lg p-2 border border-blue-500/30">
        <div className="text-xs text-blue-400">
          <div>View: {activeView === '3d-process' ? 'Court Process' : 'Jurisdictions'}</div>
          <div>Type: {activeView === '3d-process' ? processType : jurisdictionRegion}</div>
          <div>Status: {isAnimating ? 'Animated' : 'Static'}</div>
        </div>
      </div>

      {/* Help Overlay */}
      <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 bg-black/80 backdrop-blur-sm rounded-lg p-3 border border-yellow-500/30">
        <div className="text-center">
          <div className="text-yellow-400 font-semibold text-sm mb-1">🎯 Perfect 3D Legal Visualization</div>
          <div className="text-xs text-gray-300">
            Interactive 3D court processes & jurisdictional maps with R3F
          </div>
        </div>
      </div>
    </div>
  );
};

export default Perfect3DLegalVisualization;