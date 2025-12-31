import { createContext, useContext, useState, useCallback, ReactNode } from 'react'

type UserRole = 'admin' | 'analyst' | 'demo'

interface User {
  email: string
  role: UserRole
  name: string
}

interface AuthContextType {
  user: User | null
  isAuthenticated: boolean
  isAdmin: boolean
  login: (email: string, password: string) => Promise<boolean>
  logout: () => void
}

const AuthContext = createContext<AuthContextType | null>(null)

// Hardcoded credentials from credentials.md
const CREDENTIALS: Record<string, { password: string; role: UserRole; name: string }> = {
  'admin@nis.gov.in': {
    password: 'admin123',
    role: 'admin',
    name: 'Admin User'
  },
  'analyst@nis.gov.in': {
    password: 'analyst123',
    role: 'analyst',
    name: 'Senior Analyst'
  },
  'demo@nis.gov.in': {
    password: 'demo123',
    role: 'demo',
    name: 'Demo User'
  }
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(() => {
    const stored = localStorage.getItem('nis_user')
    return stored ? JSON.parse(stored) : null
  })

  const login = useCallback(async (email: string, password: string): Promise<boolean> => {
    const credential = CREDENTIALS[email.toLowerCase()]
    
    if (!credential || credential.password !== password) {
      return false
    }

    const userData: User = {
      email: email.toLowerCase(),
      role: credential.role,
      name: credential.name
    }
    
    setUser(userData)
    localStorage.setItem('nis_user', JSON.stringify(userData))
    return true
  }, [])

  const logout = useCallback(() => {
    setUser(null)
    localStorage.removeItem('nis_user')
  }, [])

  const value: AuthContextType = {
    user,
    isAuthenticated: !!user,
    isAdmin: user?.role === 'admin',
    login,
    logout
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth(): AuthContextType {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
