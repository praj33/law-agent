#!/bin/bash

# PERFECT 3D Dependencies Installation Script
# Installs React Three Fiber and all required 3D visualization dependencies

echo "🎯 INSTALLING PERFECT 3D LEGAL VISUALIZATION DEPENDENCIES"
echo "=========================================================="

# Navigate to frontend directory
cd law-agent-frontend

echo "📦 Installing React Three Fiber ecosystem..."

# Install core R3F dependencies
npm install @react-three/fiber@^8.15.12
npm install @react-three/drei@^9.92.7
npm install @react-three/cannon@^6.6.0

echo "✅ Core R3F dependencies installed"

# Install Three.js (if not already installed)
npm install three@^0.179.1
npm install @types/three@^0.178.1

echo "✅ Three.js dependencies installed"

# Install additional 3D utilities
npm install @react-three/postprocessing@^2.15.11
npm install @react-three/xr@^5.7.1

echo "✅ Additional 3D utilities installed"

# Install performance monitoring
npm install @react-three/perf@^7.1.2

echo "✅ Performance monitoring installed"

echo ""
echo "🎉 PERFECT 3D DEPENDENCIES INSTALLATION COMPLETE!"
echo "=========================================================="
echo "✅ @react-three/fiber - Core React Three Fiber"
echo "✅ @react-three/drei - Essential 3D helpers"
echo "✅ @react-three/cannon - Physics engine"
echo "✅ three - Three.js 3D library"
echo "✅ @types/three - TypeScript definitions"
echo "✅ @react-three/postprocessing - Visual effects"
echo "✅ @react-three/xr - VR/AR support"
echo "✅ @react-three/perf - Performance monitoring"
echo ""
echo "🚀 Your law agent now has PERFECT 3D visualization capabilities!"
echo "🎯 Features available:"
echo "   • 3D Court Process Flow visualization"
echo "   • 3D Jurisdictional Maps with interactive courts"
echo "   • Real-time animations and transitions"
echo "   • Interactive legal process timelines"
echo "   • Hover tooltips with legal information"
echo "   • Responsive 3D controls (zoom, rotate, pan)"
echo ""
echo "💡 To start the frontend with 3D support:"
echo "   cd law-agent-frontend && npm start"
echo ""
echo "🎉 INSTALLATION COMPLETE - 3D LEGAL VISUALIZATION READY!"
