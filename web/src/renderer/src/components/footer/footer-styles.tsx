import { SystemStyleObject } from '@chakra-ui/react';

interface FooterStyles {
  container: (isCollapsed: boolean) => SystemStyleObject
  toggleButton: SystemStyleObject
  actionButton: SystemStyleObject
  input: SystemStyleObject
  attachButton: SystemStyleObject
}

interface AIIndicatorStyles {
  container: SystemStyleObject
  text: SystemStyleObject
}

export const footerStyles: {
  footer: FooterStyles
  aiIndicator: AIIndicatorStyles
} = {
  footer: {
    container: (isCollapsed) => ({
      bg: isCollapsed ? 'transparent' : 'var(--app-panel-strong)',
      borderTopRadius: isCollapsed ? 'none' : 'lg',
      transform: isCollapsed ? 'translateY(calc(100% - 24px))' : 'translateY(0)',
      transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
      height: '100%',
      position: 'relative',
      overflow: isCollapsed ? 'visible' : 'hidden',
      pb: '4',
      backdropFilter: 'blur(16px)',
      boxShadow: 'var(--app-shadow)',
      animation: 'appFadeUp 640ms ease-out',
    }),
    toggleButton: {
      height: '24px',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      cursor: 'pointer',
      color: 'var(--app-text-muted)',
      _hover: { color: 'var(--app-text)' },
      bg: 'transparent',
      transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
    },
    actionButton: {
      borderRadius: '12px',
      width: '50px',
      height: '50px',
      minW: '50px',
      border: '1px solid',
      borderColor: 'rgba(255, 255, 255, 0.12)',
      boxShadow: '0 10px 20px rgba(0, 0, 0, 0.25)',
      transition: 'transform 0.2s ease, box-shadow 0.2s ease',
      _hover: {
        transform: 'translateY(-1px)',
        boxShadow: '0 14px 24px rgba(0, 0, 0, 0.28)',
      },
    },
    input: {
      bg: 'rgba(255, 255, 255, 0.06)',
      border: 'none',
      height: '80px',
      borderRadius: '12px',
      fontSize: '18px',
      pl: '12',
      pr: '4',
      color: 'var(--app-text)',
      _placeholder: {
        color: 'var(--app-text-muted)',
      },
      _focus: {
        border: 'none',
        bg: 'rgba(255, 255, 255, 0.08)',
      },
      resize: 'none',
      minHeight: '80px',
      maxHeight: '80px',
      py: '0',
      display: 'flex',
      alignItems: 'center',
      paddingTop: '28px',
      lineHeight: '1.4',
    },
    attachButton: {
      position: 'absolute',
      left: '1',
      top: '50%',
      transform: 'translateY(-50%)',
      color: 'var(--app-text-muted)',
      zIndex: 2,
      _hover: {
        bg: 'transparent',
        color: 'var(--app-text)',
      },
    },
  },
  aiIndicator: {
    container: {
      background: 'linear-gradient(135deg, var(--app-accent), #7ee3f1)',
      color: '#0b1116',
      width: '110px',
      height: '30px',
      borderRadius: '12px',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      boxShadow: '0 10px 18px rgba(0, 0, 0, 0.18)',
      overflow: 'hidden',
    },
    text: {
      fontSize: '12px',
      whiteSpace: 'nowrap',
      overflow: 'hidden',
      textOverflow: 'ellipsis',
    },
  },
};
