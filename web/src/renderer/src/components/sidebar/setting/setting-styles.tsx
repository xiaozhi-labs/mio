const isElectron = window.api !== undefined;
export const settingStyles = {
  settingUI: {
    container: {
      width: '100%',
      height: '100%',
      p: 4,
      gap: 4,
      position: 'relative',
      overflowY: 'auto',
      css: {
        '&::-webkit-scrollbar': {
          width: '4px',
        },
        '&::-webkit-scrollbar-track': {
          bg: 'var(--app-panel-weak)',
          borderRadius: 'full',
        },
        '&::-webkit-scrollbar-thumb': {
          bg: 'rgba(255, 255, 255, 0.28)',
          borderRadius: 'full',
        },
      },
    },
    header: {
      width: '100%',
      display: 'flex',
      alignItems: 'center',
      gap: 1,
    },
    title: {
      ml: 4,
      fontSize: 'lg',
      fontWeight: 'bold',
    },
    tabs: {
      root: {
        width: '100%',
        variant: 'plain' as const,
        colorPalette: 'gray',
      },
      content: {},
      trigger: {
        color: 'var(--app-text-muted)',
        _selected: {
          color: 'var(--app-text)',
        },
        _hover: {
          color: 'var(--app-text)',
        },
      },
      list: {
        display: 'flex',
        justifyContent: 'flex-start',
        width: '100%',
        borderBottom: '1px solid',
        borderColor: 'var(--app-border)',
        mb: 4,
        pl: 0,
      },
    },
    footer: {
      width: '100%',
      display: 'flex',
      justifyContent: 'flex-end',
      gap: 2,
      mt: 'auto',
      pt: 4,
      borderTop: '1px solid',
      borderColor: 'var(--app-border)',
    },
    drawerContent: {
      bg: 'var(--app-panel-strong)',
      maxWidth: '440px',
      height: isElectron ? 'calc(100vh - 30px)' : '100vh',
      borderLeft: '1px solid',
      borderColor: 'var(--app-border)',
    },
    drawerHeader: {
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      width: '100%',
      position: 'relative',
      px: 6,
      py: 4,
    },
    drawerTitle: {
      color: 'var(--app-text)',
      fontSize: 'lg',
      fontWeight: 'semibold',
    },
    closeButton: {
      position: 'absolute',
      right: 1,
      top: 1,
      color: 'var(--app-text)',

    },
  },
  general: {
    container: {
      align: 'stretch',
      gap: 6,
      p: 4,
    },
    field: {
      label: {
        color: 'var(--app-text)',
      },
    },
    select: {
      root: {
        colorPalette: 'gray',
        bg: 'rgba(255, 255, 255, 0.06)',
      },
      trigger: {
        bg: 'rgba(255, 255, 255, 0.06)',
      },
      content: {
        bg: 'var(--app-panel-strong)',
        color: 'var(--app-text)',
        borderColor: 'var(--app-border)',
      },
      item: {
        color: 'var(--app-text)',
        _hover: {
          bg: 'rgba(255, 255, 255, 0.08)',
        },
        _highlighted: {
          bg: 'rgba(255, 255, 255, 0.12)',
        },
        _selected: {
          bg: 'rgba(255, 255, 255, 0.16)',
        },
      },
    },
    input: {
      bg: 'rgba(255, 255, 255, 0.06)',
    },
    buttonGroup: {
      gap: 4,
      width: '100%',
    },
    button: {
      width: '50%',
      variant: 'outline' as const,
      bg: 'var(--app-accent-3)',
      color: '#0b1116',
      _hover: {
        bg: 'rgba(122, 162, 255, 0.75)',
      },
    },
    fieldLabel: {
      fontSize: '14px',
      color: 'var(--app-text-muted)',
    },
  },
  common: {
    field: {
      orientation: 'horizontal' as const,
    },
    fieldLabel: {
      fontSize: 'sm',
      color: 'var(--app-text)',
      whiteSpace: 'nowrap' as const,
    },
    switch: {
      size: 'md' as const,
      colorPalette: 'blue' as const,
      variant: 'solid' as const,
    },
    numberInput: {
      root: {
        pattern: '[0-9]*\\.?[0-9]*',
        inputMode: 'decimal' as const,
      },
      input: {
        bg: 'rgba(255, 255, 255, 0.06)',
        borderColor: 'var(--app-border)',
        _hover: {
          bg: 'rgba(255, 255, 255, 0.12)',
        },
      },
    },
    container: {
      gap: 8,
      maxW: 'sm',
      css: { '--field-label-width': '120px' },
    },
    input: {
      bg: 'rgba(255, 255, 255, 0.06)',
      borderColor: 'var(--app-border)',
      _hover: {
        bg: 'rgba(255, 255, 255, 0.12)',
      },
    },
  },
  live2d: {
    container: {
      gap: 8,
      maxW: 'sm',
      css: { '--field-label-width': '120px' },
    },
    emotionMap: {
      title: {
        fontWeight: 'bold',
        mb: 4,
      },
      entry: {
        mb: 2,
      },
      button: {
        colorPalette: 'blue',
        mt: 2,
      },
      deleteButton: {
        colorPalette: 'red',
      },
    },
  },
};
