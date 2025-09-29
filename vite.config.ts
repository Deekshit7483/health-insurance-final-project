import { defineConfig } from 'vite';<<<<<<< HEAD

import react from '@vitejs/plugin-react-swc';

import path from 'path';  import { defineConfig } from 'vite';

  import react from '@vitejs/plugin-react-swc';

export default defineConfig({  import path from 'path';

  plugins: [react()],

  resolve: {  export default defineConfig({

    extensions: ['.js', '.jsx', '.ts', '.tsx', '.json'],    plugins: [react()],

    alias: {    resolve: {

      'vaul@1.1.2': 'vaul',      extensions: ['.js', '.jsx', '.ts', '.tsx', '.json'],

      'sonner@2.0.3': 'sonner',      alias: {

      'recharts@2.15.2': 'recharts',        'vaul@1.1.2': 'vaul',

      'react-resizable-panels@2.1.7': 'react-resizable-panels',        'sonner@2.0.3': 'sonner',

      'react-hook-form@7.55.0': 'react-hook-form',        'recharts@2.15.2': 'recharts',

      'react-day-picker@8.10.1': 'react-day-picker',        'react-resizable-panels@2.1.7': 'react-resizable-panels',

      'next-themes@0.4.6': 'next-themes',        'react-hook-form@7.55.0': 'react-hook-form',

      'lucide-react@0.487.0': 'lucide-react',        'react-day-picker@8.10.1': 'react-day-picker',

      'input-otp@1.4.2': 'input-otp',        'next-themes@0.4.6': 'next-themes',

      'embla-carousel-react@8.6.0': 'embla-carousel-react',        'lucide-react@0.487.0': 'lucide-react',

      'cmdk@1.1.1': 'cmdk',        'input-otp@1.4.2': 'input-otp',

      'class-variance-authority@0.7.1': 'class-variance-authority',        'embla-carousel-react@8.6.0': 'embla-carousel-react',

      '@radix-ui/react-tooltip@1.1.8': '@radix-ui/react-tooltip',        'cmdk@1.1.1': 'cmdk',

      '@radix-ui/react-toggle@1.1.2': '@radix-ui/react-toggle',        'class-variance-authority@0.7.1': 'class-variance-authority',

      '@radix-ui/react-toggle-group@1.1.2': '@radix-ui/react-toggle-group',        '@radix-ui/react-tooltip@1.1.8': '@radix-ui/react-tooltip',

      '@radix-ui/react-tabs@1.1.3': '@radix-ui/react-tabs',        '@radix-ui/react-toggle@1.1.2': '@radix-ui/react-toggle',

      '@radix-ui/react-switch@1.1.3': '@radix-ui/react-switch',        '@radix-ui/react-toggle-group@1.1.2': '@radix-ui/react-toggle-group',

      '@radix-ui/react-slot@1.1.2': '@radix-ui/react-slot',        '@radix-ui/react-tabs@1.1.3': '@radix-ui/react-tabs',

      '@radix-ui/react-slider@1.2.3': '@radix-ui/react-slider',        '@radix-ui/react-switch@1.1.3': '@radix-ui/react-switch',

      '@radix-ui/react-separator@1.1.2': '@radix-ui/react-separator',        '@radix-ui/react-slot@1.1.2': '@radix-ui/react-slot',

      '@radix-ui/react-select@2.1.6': '@radix-ui/react-select',        '@radix-ui/react-slider@1.2.3': '@radix-ui/react-slider',

      '@radix-ui/react-scroll-area@1.2.3': '@radix-ui/react-scroll-area',        '@radix-ui/react-separator@1.1.2': '@radix-ui/react-separator',

      '@radix-ui/react-radio-group@1.2.3': '@radix-ui/react-radio-group',        '@radix-ui/react-select@2.1.6': '@radix-ui/react-select',

      '@radix-ui/react-progress@1.1.2': '@radix-ui/react-progress',        '@radix-ui/react-scroll-area@1.2.3': '@radix-ui/react-scroll-area',

      '@radix-ui/react-popover@1.1.6': '@radix-ui/react-popover',        '@radix-ui/react-radio-group@1.2.3': '@radix-ui/react-radio-group',

      '@radix-ui/react-navigation-menu@1.2.5': '@radix-ui/react-navigation-menu',        '@radix-ui/react-progress@1.1.2': '@radix-ui/react-progress',

      '@radix-ui/react-menubar@1.1.6': '@radix-ui/react-menubar',        '@radix-ui/react-popover@1.1.6': '@radix-ui/react-popover',

      '@radix-ui/react-label@2.1.2': '@radix-ui/react-label',        '@radix-ui/react-navigation-menu@1.2.5': '@radix-ui/react-navigation-menu',

      '@radix-ui/react-hover-card@1.1.6': '@radix-ui/react-hover-card',        '@radix-ui/react-menubar@1.1.6': '@radix-ui/react-menubar',

      '@radix-ui/react-dropdown-menu@2.1.6': '@radix-ui/react-dropdown-menu',        '@radix-ui/react-label@2.1.2': '@radix-ui/react-label',

      '@radix-ui/react-dialog@1.1.6': '@radix-ui/react-dialog',        '@radix-ui/react-hover-card@1.1.6': '@radix-ui/react-hover-card',

      '@radix-ui/react-context-menu@2.2.6': '@radix-ui/react-context-menu',        '@radix-ui/react-dropdown-menu@2.1.6': '@radix-ui/react-dropdown-menu',

      '@radix-ui/react-collapsible@1.1.3': '@radix-ui/react-collapsible',        '@radix-ui/react-dialog@1.1.6': '@radix-ui/react-dialog',

      '@radix-ui/react-checkbox@1.1.4': '@radix-ui/react-checkbox',        '@radix-ui/react-context-menu@2.2.6': '@radix-ui/react-context-menu',

      '@radix-ui/react-avatar@1.1.3': '@radix-ui/react-avatar',        '@radix-ui/react-collapsible@1.1.3': '@radix-ui/react-collapsible',

      '@radix-ui/react-aspect-ratio@1.1.2': '@radix-ui/react-aspect-ratio',        '@radix-ui/react-checkbox@1.1.4': '@radix-ui/react-checkbox',

      '@radix-ui/react-alert-dialog@1.1.6': '@radix-ui/react-alert-dialog',        '@radix-ui/react-avatar@1.1.3': '@radix-ui/react-avatar',

      '@radix-ui/react-accordion@1.2.3': '@radix-ui/react-accordion',        '@radix-ui/react-aspect-ratio@1.1.2': '@radix-ui/react-aspect-ratio',

      '@': path.resolve(__dirname, './src'),        '@radix-ui/react-alert-dialog@1.1.6': '@radix-ui/react-alert-dialog',

    },        '@radix-ui/react-accordion@1.2.3': '@radix-ui/react-accordion',

  },        '@': path.resolve(__dirname, './src'),

  build: {      },

    target: 'esnext',    },

    outDir: 'build',    build: {

  },      target: 'esnext',

  server: {      outDir: 'build',

    port: 3000,    },

    open: true,    server: {

  },      port: 3000,

});      open: true,
    },
  });
=======
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    open: true,
  },
})
>>>>>>> 7110398f001cfc4d9dd0532b08169a486d50900b
