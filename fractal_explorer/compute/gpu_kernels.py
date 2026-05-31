"""
CUDA kernels for GPU-accelerated fractal computation using CuPy.
"""

# GPU kernels will only be loaded if CuPy is available
GPU_AVAILABLE = False
cp = None

try:
    import cupy as cp
    GPU_AVAILABLE = True
except ImportError:
    pass


if GPU_AVAILABLE:
    # Mandelbrot kernel
    mandelbrot_kernel = cp.RawKernel(r'''
    extern "C" __global__
    void mandelbrot(float* output, int width, int height,
                    double x_min, double x_max, double y_min, double y_max,
                    int max_iter) {
        int px = blockIdx.x * blockDim.x + threadIdx.x;
        int py = blockIdx.y * blockDim.y + threadIdx.y;

        if (px >= width || py >= height) return;

        double x0 = x_min + (x_max - x_min) * px / width;
        double y0 = y_max - (y_max - y_min) * py / height;  // Flip Y for correct orientation

        double x = 0.0, y = 0.0;
        int iter = 0;

        while (x*x + y*y <= 4.0 && iter < max_iter) {
            double xtemp = x*x - y*y + x0;
            y = 2.0*x*y + y0;
            x = xtemp;
            iter++;
        }

        // Smooth coloring
        float smooth_iter = (float)iter;
        if (iter < max_iter) {
            float log_zn = logf((float)(x*x + y*y)) / 2.0f;
            float nu = logf(log_zn / logf(2.0f)) / logf(2.0f);
            smooth_iter = iter + 1.0f - nu;
        }

        output[py * width + px] = smooth_iter;
    }
    ''', 'mandelbrot')

    # Julia kernel
    julia_kernel = cp.RawKernel(r'''
    extern "C" __global__
    void julia(float* output, int width, int height,
               double x_min, double x_max, double y_min, double y_max,
               double c_re, double c_im, int max_iter) {
        int px = blockIdx.x * blockDim.x + threadIdx.x;
        int py = blockIdx.y * blockDim.y + threadIdx.y;

        if (px >= width || py >= height) return;

        double x = x_min + (x_max - x_min) * px / width;
        double y = y_max - (y_max - y_min) * py / height;

        int iter = 0;

        while (x*x + y*y <= 4.0 && iter < max_iter) {
            double xtemp = x*x - y*y + c_re;
            y = 2.0*x*y + c_im;
            x = xtemp;
            iter++;
        }

        // Smooth coloring
        float smooth_iter = (float)iter;
        if (iter < max_iter) {
            float log_zn = logf((float)(x*x + y*y)) / 2.0f;
            float nu = logf(log_zn / logf(2.0f)) / logf(2.0f);
            smooth_iter = iter + 1.0f - nu;
        }

        output[py * width + px] = smooth_iter;
    }
    ''', 'julia')

    # Burning Ship kernel
    burning_ship_kernel = cp.RawKernel(r'''
    extern "C" __global__
    void burning_ship(float* output, int width, int height,
                      double x_min, double x_max, double y_min, double y_max,
                      int max_iter) {
        int px = blockIdx.x * blockDim.x + threadIdx.x;
        int py = blockIdx.y * blockDim.y + threadIdx.y;

        if (px >= width || py >= height) return;

        double x0 = x_min + (x_max - x_min) * px / width;
        double y0 = y_max - (y_max - y_min) * py / height;  // Flip Y for correct orientation

        double x = 0.0, y = 0.0;
        int iter = 0;

        while (x*x + y*y <= 4.0 && iter < max_iter) {
            // Take absolute values before squaring
            double xtemp = x*x - y*y + x0;
            y = fabs(2.0*x*y) + y0;
            x = fabs(xtemp);
            iter++;
        }

        // Smooth coloring
        float smooth_iter = (float)iter;
        if (iter < max_iter) {
            float log_zn = logf((float)(x*x + y*y)) / 2.0f;
            float nu = logf(log_zn / logf(2.0f)) / logf(2.0f);
            smooth_iter = iter + 1.0f - nu;
        }

        output[py * width + px] = smooth_iter;
    }
    ''', 'burning_ship')

    # Tricorn (Mandelbar) kernel
    tricorn_kernel = cp.RawKernel(r'''
    extern "C" __global__
    void tricorn(float* output, int width, int height,
                 double x_min, double x_max, double y_min, double y_max,
                 int max_iter) {
        int px = blockIdx.x * blockDim.x + threadIdx.x;
        int py = blockIdx.y * blockDim.y + threadIdx.y;

        if (px >= width || py >= height) return;

        double x0 = x_min + (x_max - x_min) * px / width;
        double y0 = y_max - (y_max - y_min) * py / height;

        double x = 0.0, y = 0.0;
        int iter = 0;

        while (x*x + y*y <= 4.0 && iter < max_iter) {
            // Use conjugate: (x - iy)^2 + c = x^2 - y^2 - 2ixy + c
            double xtemp = x*x - y*y + x0;
            y = -2.0*x*y + y0;  // Negated for conjugate
            x = xtemp;
            iter++;
        }

        // Smooth coloring
        float smooth_iter = (float)iter;
        if (iter < max_iter) {
            float log_zn = logf((float)(x*x + y*y)) / 2.0f;
            float nu = logf(log_zn / logf(2.0f)) / logf(2.0f);
            smooth_iter = iter + 1.0f - nu;
        }

        output[py * width + px] = smooth_iter;
    }
    ''', 'tricorn')

    # Phoenix fractal kernel
    phoenix_kernel = cp.RawKernel(r'''
    extern "C" __global__
    void phoenix(float* output, int width, int height,
                 double x_min, double x_max, double y_min, double y_max,
                 double p_re, double p_im, int max_iter) {
        int px = blockIdx.x * blockDim.x + threadIdx.x;
        int py = blockIdx.y * blockDim.y + threadIdx.y;

        if (px >= width || py >= height) return;

        // For Phoenix, the starting point is the pixel coordinate
        double x = x_min + (x_max - x_min) * px / width;
        double y = y_max - (y_max - y_min) * py / height;

        // z(n+1) = z(n)^2 + p_re + p_im * z(n-1)
        double prev_x = 0.0, prev_y = 0.0;
        int iter = 0;

        while (x*x + y*y <= 4.0 && iter < max_iter) {
            double xtemp = x*x - y*y + p_re + p_im * prev_x;
            double ytemp = 2.0*x*y + p_im * prev_y;
            prev_x = x;
            prev_y = y;
            x = xtemp;
            y = ytemp;
            iter++;
        }

        // Smooth coloring
        float smooth_iter = (float)iter;
        if (iter < max_iter) {
            float log_zn = logf((float)(x*x + y*y)) / 2.0f;
            float nu = logf(log_zn / logf(2.0f)) / logf(2.0f);
            smooth_iter = iter + 1.0f - nu;
        }

        output[py * width + px] = smooth_iter;
    }
    ''', 'phoenix')

    # Newton fractal kernel for z^3 - 1 = 0
    newton_kernel = cp.RawKernel(r'''
    extern "C" __global__
    void newton(float* output, int width, int height,
                double x_min, double x_max, double y_min, double y_max,
                int max_iter, double tolerance) {
        int px = blockIdx.x * blockDim.x + threadIdx.x;
        int py = blockIdx.y * blockDim.y + threadIdx.y;

        if (px >= width || py >= height) return;

        double zr = x_min + (x_max - x_min) * px / width;
        double zi = y_max - (y_max - y_min) * py / height;

        // Roots of z^3 - 1 = 0
        double root1_r = 1.0, root1_i = 0.0;
        double root2_r = -0.5, root2_i = 0.86602540378;   // sqrt(3)/2
        double root3_r = -0.5, root3_i = -0.86602540378;

        int iter = 0;
        int root = 0;

        while (iter < max_iter) {
            // f(z) = z^3 - 1
            // f'(z) = 3z^2
            // z_new = z - f(z)/f'(z) = z - (z^3 - 1)/(3z^2)

            double zr2 = zr * zr;
            double zi2 = zi * zi;
            double zr3 = zr * zr2 - 3.0 * zr * zi2;
            double zi3 = 3.0 * zr2 * zi - zi * zi2;

            // 3z^2
            double denom_r = 3.0 * (zr2 - zi2);
            double denom_i = 6.0 * zr * zi;
            double denom_mag2 = denom_r * denom_r + denom_i * denom_i;

            if (denom_mag2 < 1e-20) break;

            // (z^3 - 1) / (3z^2)
            double num_r = zr3 - 1.0;
            double num_i = zi3;

            double div_r = (num_r * denom_r + num_i * denom_i) / denom_mag2;
            double div_i = (num_i * denom_r - num_r * denom_i) / denom_mag2;

            zr = zr - div_r;
            zi = zi - div_i;

            // Check convergence to roots
            double d1 = (zr - root1_r) * (zr - root1_r) + (zi - root1_i) * (zi - root1_i);
            double d2 = (zr - root2_r) * (zr - root2_r) + (zi - root2_i) * (zi - root2_i);
            double d3 = (zr - root3_r) * (zr - root3_r) + (zi - root3_i) * (zi - root3_i);

            double tol2 = tolerance * tolerance;
            if (d1 < tol2) { root = 1; break; }
            if (d2 < tol2) { root = 2; break; }
            if (d3 < tol2) { root = 3; break; }

            iter++;
        }

        // Combine root and iteration for coloring
        // Root determines hue region, iterations determine brightness
        float value = (float)root + (float)iter / (float)max_iter;
        output[py * width + px] = value;
    }
    ''', 'newton')


class GPUCompute:
    """GPU-accelerated fractal computation using CuPy/CUDA."""

    # Optimal block size for most GPUs (32x32 = 1024 threads)
    BLOCK_SIZE = 32

    def __init__(self):
        if not GPU_AVAILABLE:
            raise RuntimeError("CuPy/CUDA is not available")
        # Get device name using runtime API (compatible with CuPy 13+)
        try:
            props = cp.cuda.runtime.getDeviceProperties(0)
            name = props['name']
            self.device_name = name.decode() if isinstance(name, bytes) else name
        except Exception:
            self.device_name = f"CUDA Device {cp.cuda.Device(0).id}"

        # Pre-allocate output buffers for common sizes to reduce allocation overhead
        self._output_cache = {}

    def _get_output_buffer(self, height: int, width: int) -> 'cp.ndarray':
        """Get or create output buffer for given size."""
        key = (height, width)
        if key not in self._output_cache:
            self._output_cache[key] = cp.zeros((height, width), dtype=cp.float32)
        return self._output_cache[key]

    def compute_mandelbrot(self, width: int, height: int,
                          x_min: float, x_max: float,
                          y_min: float, y_max: float,
                          max_iter: int) -> 'cp.ndarray':
        """Compute Mandelbrot set on GPU."""
        output = self._get_output_buffer(height, width)

        bs = self.BLOCK_SIZE
        block = (bs, bs)
        grid = ((width + bs - 1) // bs, (height + bs - 1) // bs)

        mandelbrot_kernel(grid, block, (
            output, width, height,
            x_min, x_max, y_min, y_max, max_iter
        ))

        # Synchronize to ensure computation is complete before returning
        cp.cuda.Stream.null.synchronize()

        return output

    def compute_julia(self, width: int, height: int,
                     x_min: float, x_max: float,
                     y_min: float, y_max: float,
                     c_re: float, c_im: float,
                     max_iter: int) -> 'cp.ndarray':
        """Compute Julia set on GPU."""
        output = self._get_output_buffer(height, width)

        bs = self.BLOCK_SIZE
        block = (bs, bs)
        grid = ((width + bs - 1) // bs, (height + bs - 1) // bs)

        julia_kernel(grid, block, (
            output, width, height,
            x_min, x_max, y_min, y_max,
            c_re, c_im, max_iter
        ))

        cp.cuda.Stream.null.synchronize()

        return output

    def compute_burning_ship(self, width: int, height: int,
                             x_min: float, x_max: float,
                             y_min: float, y_max: float,
                             max_iter: int) -> 'cp.ndarray':
        """Compute Burning Ship fractal on GPU."""
        output = self._get_output_buffer(height, width)

        bs = self.BLOCK_SIZE
        block = (bs, bs)
        grid = ((width + bs - 1) // bs, (height + bs - 1) // bs)

        burning_ship_kernel(grid, block, (
            output, width, height,
            x_min, x_max, y_min, y_max, max_iter
        ))

        cp.cuda.Stream.null.synchronize()

        return output

    def compute_tricorn(self, width: int, height: int,
                       x_min: float, x_max: float,
                       y_min: float, y_max: float,
                       max_iter: int) -> 'cp.ndarray':
        """Compute Tricorn (Mandelbar) fractal on GPU."""
        output = self._get_output_buffer(height, width)

        bs = self.BLOCK_SIZE
        block = (bs, bs)
        grid = ((width + bs - 1) // bs, (height + bs - 1) // bs)

        tricorn_kernel(grid, block, (
            output, width, height,
            x_min, x_max, y_min, y_max, max_iter
        ))

        cp.cuda.Stream.null.synchronize()

        return output

    def compute_phoenix(self, width: int, height: int,
                       x_min: float, x_max: float,
                       y_min: float, y_max: float,
                       p_re: float, p_im: float,
                       max_iter: int) -> 'cp.ndarray':
        """Compute Phoenix fractal on GPU."""
        output = self._get_output_buffer(height, width)

        bs = self.BLOCK_SIZE
        block = (bs, bs)
        grid = ((width + bs - 1) // bs, (height + bs - 1) // bs)

        phoenix_kernel(grid, block, (
            output, width, height,
            x_min, x_max, y_min, y_max,
            p_re, p_im, max_iter
        ))

        cp.cuda.Stream.null.synchronize()

        return output

    def compute_newton(self, width: int, height: int,
                      x_min: float, x_max: float,
                      y_min: float, y_max: float,
                      max_iter: int,
                      tolerance: float = 1e-6) -> 'cp.ndarray':
        """Compute Newton fractal on GPU."""
        output = self._get_output_buffer(height, width)

        bs = self.BLOCK_SIZE
        block = (bs, bs)
        grid = ((width + bs - 1) // bs, (height + bs - 1) // bs)

        newton_kernel(grid, block, (
            output, width, height,
            x_min, x_max, y_min, y_max,
            max_iter, tolerance
        ))

        cp.cuda.Stream.null.synchronize()

        return output

    @staticmethod
    def to_numpy(gpu_array: 'cp.ndarray'):
        """Convert GPU array to numpy array."""
        return cp.asnumpy(gpu_array)

    @staticmethod
    def apply_colormap(iterations: 'cp.ndarray', colormap_lut: 'cp.ndarray', max_iter: int):
        """Apply colormap on GPU."""
        # Normalize iterations
        normalized = cp.clip(iterations / max_iter, 0, 1)
        indices = (normalized * 255).astype(cp.uint8)

        # Apply lookup table
        rgba = colormap_lut[indices]
        return cp.asnumpy(rgba)
