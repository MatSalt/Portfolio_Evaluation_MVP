// src/utils/__tests__/api.test.ts
import { validateImageFile, fileToBase64 } from '../api'

// Mock fetch globally
global.fetch = jest.fn()

describe('API Utils', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  describe('validateImageFile', () => {
    it('should validate PNG files', () => {
      const file = new File(['test'], 'test.png', { type: 'image/png' })
      const result = validateImageFile(file)
      expect(result.isValid).toBe(true)
    })

    it('should validate JPEG files', () => {
      const file = new File(['test'], 'test.jpg', { type: 'image/jpeg' })
      const result = validateImageFile(file)
      expect(result.isValid).toBe(true)
    })

    it('should reject unsupported file types', () => {
      const file = new File(['test'], 'test.gif', { type: 'image/gif' })
      const result = validateImageFile(file)
      expect(result.isValid).toBe(false)
      expect(result.error).toBe('PNG, JPEG 파일만 업로드 가능합니다.')
    })

    it('should reject files larger than 10MB', () => {
      const file = new File(['test'], 'test.jpg', { type: 'image/jpeg' })
      Object.defineProperty(file, 'size', { value: 11 * 1024 * 1024 }) // 11MB
      const result = validateImageFile(file)
      expect(result.isValid).toBe(false)
      expect(result.error).toBe('파일 크기는 10MB 이하만 허용됩니다.')
    })
  })

  describe('fileToBase64', () => {
    it('should convert file to base64', async () => {
      const file = new File(['test'], 'test.jpg', { type: 'image/jpeg' })
      const result = await fileToBase64(file)
      expect(result).toBe('data:image/jpeg;base64,test')
    })

    it('should reject on file read error', async () => {
      const file = new File(['test'], 'test.jpg', { type: 'image/jpeg' })
      const originalFileReader = global.FileReader
      
      // Mock FileReader to throw error
      global.FileReader = class {
        readAsDataURL() {
          setTimeout(() => {
            if (this.onerror) this.onerror(new Error('Read error'))
          }, 0)
        }
      } as any

      await expect(fileToBase64(file)).rejects.toThrow('파일 읽기 중 오류 발생')
      
      // Restore original FileReader
      global.FileReader = originalFileReader
    })
  })
})