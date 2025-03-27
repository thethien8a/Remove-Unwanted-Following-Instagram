import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
import random

def open_instagram_login():
    try:
        # Tạo options để cấu hình Chrome với tiếng Việt
        options = uc.ChromeOptions()
        
        # Cấu hình ngôn ngữ là tiếng Việt
        options.add_argument("--lang=vi-VN")
        options.add_argument("--accept-lang=vi-VN,vi")
        
        # Thiết lập header Accept-Language
        options.add_experimental_option('prefs', {
            'intl.accept_languages': 'vi-VN,vi'
        })
        
        # Sử dụng undetected_chromedriver với options đã cấu hình
        driver = uc.Chrome(options=options)
        
        # Thiết lập language preference qua JavaScript
        driver.execute_script(
            "Object.defineProperty(navigator, 'language', {get: function() {return 'vi-VN'}}); "
            "Object.defineProperty(navigator, 'languages', {get: function() {return ['vi-VN', 'vi']}}); "
        )
        
        # Mở trang đăng nhập Instagram
        driver.get("https://www.instagram.com/?hl=vi")
        
        # Chờ đợi trang tải hoàn toàn
        time.sleep(5)
        
        return driver
    
    except Exception as e:
        print(f"Có lỗi xảy ra khi khởi tạo trình duyệt: {str(e)}")
        if 'driver' in locals():
            driver.quit()
        return None

def get_profile_info(driver):
    try:
        # Đợi lâu hơn để đảm bảo trang đã tải hoàn toàn
        time.sleep(10)
        
        # Kiểm tra xem đã đăng nhập chưa bằng cách tìm avatar
        try:   
            # Tìm menu item "Trang cá nhân"/"Profile" (nhiều cách để tìm)
            selectors = [
                "//span[contains(text(), 'Trang cá nhân')]",  # Tiếng Việt
                "//span[text()='Trang cá nhân']",             # Tiếng Việt (chính xác)
            ]
            
            # Thử từng selector cho đến khi tìm thấy
            profile_link = None
            for selector in selectors:
                try:
                    profile_link = driver.find_element(By.XPATH, selector)
                    print(f"Đã tìm thấy liên kết với selector: {selector}")
                    break
                except:
                    continue
            
            if profile_link:
                profile_link.click()
                print("Đã nhấp vào liên kết 'Trang cá nhân'!")
            else:
                print("Không tìm thấy liên kết trang cá nhân, thử phương pháp khác...")
                # Phương pháp thay thế: Truy cập trực tiếp URL trang cá nhân
                # Lấy username từ URL hiện tại hoặc từ các phần tử khác
                try:
                    # Hoặc bạn có thể thử lấy username từ nút avatar
                    username = driver.find_element(By.XPATH, "//div[@role='button']//img[@alt]").get_attribute("alt")
                    if username:
                        username = username.split("'s")[0]  # Lấy phần trước 's trong "username's profile picture"
                        driver.get(f"https://www.instagram.com/{username}/")
                        print(f"Đã điều hướng đến trang cá nhân: {username}")
                except Exception as e:
                    print(f"Không thể xác định username: {str(e)}")
                    # Thử phương pháp cuối cùng: Truy cập trang cá nhân thông qua URL
                    driver.quit()
                    print("Đóng trình duyệt !")
        
        except Exception as e:
            print(f"Không tìm thấy avatar: {str(e)}")
            # Thử truy cập trực tiếp trang các thông tin người dùng thay thế
            driver.quit()
            print("Đóng trình duyệt !")
        
        # Đợi trang cá nhân tải
        time.sleep(3)
        
        # In URL hiện tại để kiểm tra
        print(f"URL hiện tại: {driver.current_url}")
        
        return True
        
    except Exception as e:
        print(f"Lỗi khi truy cập trang cá nhân: {str(e)}")
        return False

# Hàm để tìm danh sách người đang theo dõi
def unfollow_peoples(driver):
    try:
        
        # Tìm kiếm liên kết "Đang theo dõi" hoặc "Following"
        following_selectors = [
            "//a[contains(@href, 'following')]",
            "//a[contains(text(), 'Đang theo dõi')]",
            "//div[contains(text(), 'Đang theo dõi')]"
            "//a[contains(text(), 'người dùng')]",
        ]
        
        following_link = None
        for selector in following_selectors:
            try:
                following_link = driver.find_element(By.XPATH, selector)
                print(f"Đã tìm thấy liên kết 'Đang theo dõi' với selector: {selector}")
                break
            except:
                continue
        
        if following_link:
            
            following_link.click()
            print("Đã nhấp vào liên kết 'Đang theo dõi'!")
            time.sleep(5)
            
            following_list = []
            
            # Đợi cho dialog hiển thị
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[@role='dialog']"))
            )
            
            # Tìm container chứa danh sách
            following_container = driver.find_element(By.XPATH, "//div[@class='xyi19xy x1ccrb07 xtf3nb5 x1pc53ja x1lliihq x1iyjqo2 xs83m0k xz65tgg x1rife3k x1n2onr6']")
            
            # Scroll để tải thêm người dùng
            scroll_attempts = 1000  # Số lần scroll
            last_height = driver.execute_script("return arguments[0].scrollHeight", following_container)
            
            for _ in range(scroll_attempts):
                # Scroll xuống cuối
                driver.execute_script("arguments[0].scrollTo(0, arguments[0].scrollHeight);", following_container)
                
                # Đợi để tải thêm nội dung
                time.sleep(random.randrange(2, 4))
                
                # Tính chiều cao mới
                new_height = driver.execute_script("return arguments[0].scrollHeight", following_container)
                
                # Nếu chiều cao không thay đổi, đã đến cuối danh sách
                if new_height == last_height:
                    break
                    
                last_height = new_height
            

            # Lấy tất cả các nút bấm "Đang theo dõi"
            try:
                # Tìm tất cả các nút "Đang theo dõi" dựa trên class
                following_buttons = driver.find_elements(By.XPATH, "//button[contains(@class, '_acan') and contains(@class, '_acap') and contains(@class, '_acat')]")
                
                for button in following_buttons:
                        button.click()
                        time.sleep(2)
                        try:
                            confirm_button = WebDriverWait(driver, 5).until(
                                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Bỏ theo dõi')]"))
                            )
                            confirm_button.click()
                            print("Đã xác nhận bỏ theo dõi")
                            time.sleep(random.uniform(1, 2))
                        except Exception as e:
                            print(f"Không tìm thấy pop-up xác nhận: {e}")
                
                print(f"Đã tìm thấy {len(following_list)} người đang theo dõi")
                
            except Exception as e:
                print(f"Lỗi khi lấy danh sách người dùng: {str(e)}")
        else:
            print("Không tìm thấy liên kết 'Đang theo dõi'")
            
    except Exception as e:
        print(f"Lỗi khi lấy danh sách người đang theo dõi: {str(e)}")

# Sử dụng code
if __name__ == "__main__":
    driver = open_instagram_login()
    
    if driver:
        try:
            # Thông báo cho người dùng đăng nhập
            print("Vui lòng đăng nhập vào tài khoản Instagram của bạn...")
            
            # Đợi người dùng đăng nhập thủ công
            input("Nhấn Enter sau khi đã đăng nhập để tiếp tục...")
            
            # Kiểm tra xem đã đăng nhập thành công chưa
            try:
                # Đợi tối đa 10 giây để tìm một phần tử chỉ xuất hiện sau khi đăng nhập
                print("Đăng nhập thành công!")
                
                # Truy cập trang cá nhân
                success = get_profile_info(driver)
                
                if success:
                    print("Đã truy cập trang cá nhân thành công!")
                    unfollow_peoples(driver)
                else:
                    print("Không thể truy cập trang cá nhân. Vui lòng kiểm tra lại.")
            
            except TimeoutException:
                print("Không phát hiện đăng nhập thành công. Vui lòng thử lại.")
        
        except Exception as e:
            print(f"Lỗi không mong muốn: {str(e)}")
        
        finally:
            # Đợi người dùng kiểm tra
            input("Nhấn Enter để đóng trình duyệt...")
            driver.quit()
    else:
        print("Không thể khởi tạo trình duyệt. Vui lòng kiểm tra lại cài đặt.")